"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import ValidationError

from app.db.execution import (
    execute_sql_delete,
    execute_sql_insert,
    execute_sql_select,
    execute_sql_update,
    execute_sql_upsert,
)
from app.db.version import get_db_version
from app.core.exceptions import InvalidParametersError
from app.schemas.epa.dscenario_models import (
    DscenarioCreateRequest,
    DscenarioFilterFieldsModel,
    DscenarioObjectType,
    get_dscenario_object_id_column,
    get_dscenario_table,
)
from app.services.basic_service import BasicService
from app.services.context import ServiceContext
from app.services.procedure import run_procedure
from app.utils.body import create_body_dict


class DscenarioService:
    def __init__(self, ctx: ServiceContext):
        self.ctx = ctx.with_logger(__name__)
        self._basic = BasicService(self.ctx)

    async def _object_response(self, message: str, items: List[Dict[str, Any]] | None) -> dict:
        log = self.ctx.logger or logging.getLogger(__name__)
        db_version = await get_db_version(log, self.ctx.db_manager, schema=self.ctx.schema)
        data = None if items is None else {"items": items, "count": len(items)}
        return {
            "status": "Accepted",
            "message": {"level": 3, "text": message},
            "version": {"db": db_version, "api": self.ctx.api_version},
            "body": {"form": None, "feature": None, "data": data},
        }

    async def create_dscenario(self, payload: DscenarioCreateRequest) -> dict:
        parameters = {
            "name": payload.name,
            "descript": payload.descript or "",
            "parent": payload.parent,
            "type": payload.type,
            "active": "true" if payload.active else "false",
            "expl": str(payload.expl),
        }
        body = create_body_dict(
            project_epsg=None,
            extras={"parameters": parameters},
            cur_user=self.ctx.user_id,
            device=self.ctx.device,
            lang=self.ctx.lang,
        )
        return await run_procedure(self.ctx, "gw_fct_create_dscenario_empty", body)

    async def get_dscenarios(self, filter_fields: Optional[str] = None) -> dict:
        if filter_fields:
            try:
                filter_fields_dict = json.loads(filter_fields)
                DscenarioFilterFieldsModel(data=filter_fields_dict)
            except (json.JSONDecodeError, ValidationError) as exc:
                raise InvalidParametersError(f"Invalid filterFields: {exc}") from exc
        return await self._basic.get_list("ve_cat_dscenario", filter_fields=filter_fields)

    async def select_dscenario(self, dscenario_id: int) -> dict:
        rows, _ = await execute_sql_upsert(
            log=self.ctx.logger,
            db_manager=self.ctx.db_manager,
            table_name="selector_inp_dscenario",
            data={"dscenario_id": dscenario_id},
            where_data={"cur_user": self.ctx.user_id},
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        return await self._object_response("Dscenario selected", rows)

    async def delete_dscenario(self, dscenario_id: int) -> dict:
        status = await execute_sql_delete(
            log=self.ctx.logger,
            db_manager=self.ctx.db_manager,
            table_name="ve_cat_dscenario",
            where_data={"dscenario_id": dscenario_id},
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        if not status:
            raise LookupError("Dscenario not found")
        return await self._object_response("Dscenario deleted", None)

    async def get_dscenario_objects(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        filter_fields: Optional[str] = None,
    ) -> dict:
        if filter_fields:
            try:
                merged_filters = json.loads(filter_fields)
                if not isinstance(merged_filters, dict):
                    raise InvalidParametersError("filterFields must be a JSON object")
            except (json.JSONDecodeError, ValueError) as exc:
                raise InvalidParametersError(f"Invalid filterFields: {exc}") from exc
        else:
            merged_filters = {}
        merged_filters["dscenario_id"] = {"value": dscenario_id, "filterSign": "="}
        return await self._basic.get_list(
            get_dscenario_table(object_type),
            filter_fields=json.dumps(merged_filters),
        )

    async def insert_dscenario_objects(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        objects: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> dict:
        table_name = get_dscenario_table(object_type)
        items_list = [objects] if isinstance(objects, dict) else objects
        all_rows: List[Dict[str, Any]] = []
        for obj in items_list:
            obj["dscenario_id"] = dscenario_id
            rows = await execute_sql_insert(
                log=self.ctx.logger,
                db_manager=self.ctx.db_manager,
                table_name=table_name,
                data=obj,
                schema=self.ctx.schema,
                user=self.ctx.user_id,
                db_role=self.ctx.db_role,
            )
            all_rows.extend(rows)
        return await self._object_response(f"Inserted {len(all_rows)} rows", all_rows)

    async def upsert_dscenario_objects(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        objects: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> dict:
        table_name = get_dscenario_table(object_type)
        id_column, id_type = get_dscenario_object_id_column(object_type)
        items_list = [objects] if isinstance(objects, dict) else objects
        all_rows: List[Dict[str, Any]] = []
        for obj in items_list:
            row = dict(obj)
            row.pop("dscenario_id", None)
            if id_column not in row:
                raise ValueError(f"Each object must include '{id_column}'")
            object_id = id_type(row.pop(id_column))
            where_data = {"dscenario_id": dscenario_id, id_column: object_id}
            rows, _ = await execute_sql_upsert(
                log=self.ctx.logger,
                db_manager=self.ctx.db_manager,
                table_name=table_name,
                data=row,
                where_data=where_data,
                schema=self.ctx.schema,
                user=self.ctx.user_id,
                db_role=self.ctx.db_role,
            )
            all_rows.extend(rows)
        return await self._object_response(f"Upserted {len(all_rows)} rows", all_rows)

    async def get_dscenario_object(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        object_id: str,
    ) -> dict:
        table_name = get_dscenario_table(object_type)
        id_column, id_type = get_dscenario_object_id_column(object_type)
        typed_id = id_type(object_id)
        rows = await execute_sql_select(
            log=self.ctx.logger,
            db_manager=self.ctx.db_manager,
            table_name=table_name,
            where_clause="dscenario_id = %s AND {} = %s".format(id_column),
            parameters=(dscenario_id, typed_id),
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        if not rows:
            raise LookupError("Object not found")
        return await self._object_response("Object fetched", rows)

    async def update_dscenario_object(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        object_id: str,
        data: Dict[str, Any],
    ) -> dict:
        table_name = get_dscenario_table(object_type)
        id_column, id_type = get_dscenario_object_id_column(object_type)
        typed_id = id_type(object_id)
        update_data = dict(data)
        update_data.pop("dscenario_id", None)
        update_data.pop(id_column, None)
        if not update_data:
            raise ValueError("No updatable fields provided")
        where_data = {"dscenario_id": dscenario_id, id_column: typed_id}
        rows = await execute_sql_update(
            log=self.ctx.logger,
            db_manager=self.ctx.db_manager,
            table_name=table_name,
            data=update_data,
            where_data=where_data,
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        if not rows:
            raise LookupError("Object not found")
        return await self._object_response("Object updated", rows)

    async def upsert_dscenario_object(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        object_id: str,
        data: Dict[str, Any],
    ) -> dict:
        table_name = get_dscenario_table(object_type)
        id_column, id_type = get_dscenario_object_id_column(object_type)
        typed_id = id_type(object_id)
        upsert_data = dict(data)
        upsert_data.pop("dscenario_id", None)
        upsert_data.pop(id_column, None)
        where_data = {"dscenario_id": dscenario_id, id_column: typed_id}
        rows, op = await execute_sql_upsert(
            log=self.ctx.logger,
            db_manager=self.ctx.db_manager,
            table_name=table_name,
            data=upsert_data,
            where_data=where_data,
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        message_text = "Object inserted" if op == "inserted" else "Object updated"
        return await self._object_response(message_text, rows)

    async def delete_dscenario_object(
        self,
        dscenario_id: int,
        object_type: DscenarioObjectType,
        object_id: str,
    ) -> dict:
        table_name = get_dscenario_table(object_type)
        id_column, id_type = get_dscenario_object_id_column(object_type)
        typed_id = id_type(object_id)
        where_data = {"dscenario_id": dscenario_id, id_column: typed_id}
        status = await execute_sql_delete(
            log=self.ctx.logger,
            db_manager=self.ctx.db_manager,
            table_name=table_name,
            where_data=where_data,
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        if not status:
            raise LookupError("Object not found")
        return await self._object_response("Object deleted", None)
