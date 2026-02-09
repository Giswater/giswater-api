"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

import os
import logging
import json
import asyncio
import contextvars
import time
import uuid
from logging.handlers import TimedRotatingFileHandler

from typing import Any, Dict, Literal
from datetime import date, datetime, timezone
from fastapi import FastAPI, HTTPException
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Json

from ..models.util_models import APIResponse
from ..exceptions import ProcedureError
from ..config import settings


def load_plugins(app: FastAPI):
    """
    Load plugins from the plugins directory for a specific app instance.

    Args:
        app: FastAPI app instance to register plugins to
    """
    from importlib import import_module

    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        return

    for plugin in os.listdir(plugins_dir):
        if not os.path.isdir(f"{plugins_dir}/{plugin}"):
            continue

        try:
            module = import_module(f".{plugin}", package=f"{plugins_dir}")
            module.register_plugin(app)
        except Exception as e:
            print(f"Error loading plugin {plugin}: {e}")


def create_body_dict(
    project_epsg=None,
    client_extras=None,
    form=None,
    feature=None,
    filter_fields=None,
    page_info=None,
    extras=None,
    cur_user: str | None = "anonymous",
    device: int = 4,
    lang: str = "es_ES",
) -> str:
    """
    Create request body dictionary for database functions.

    Args:
        project_epsg: Project EPSG code
        client_extras: Extra client parameters
        form: Form data
        feature: Feature data
        filter_fields: Filter fields
        extras: Extra data
        cur_user: Current user (from JWT or config)
        device: Device identifier (from X-Device header)

    Returns:
        Formatted JSON string
    """
    info_type = 1
    if cur_user == "anonymous":
        cur_user = None

    client_extras, form, feature, filter_fields, page_info, extras = _manage_body_params(
        client_extras, form, feature, filter_fields, page_info, extras
    )

    client = {"device": device, "lang": lang, "cur_user": cur_user, **client_extras}
    if info_type is not None:
        client["infoType"] = info_type
    if project_epsg is not None:
        client["epsg"] = project_epsg

    def json_default(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    json_str = json.dumps(
        {
            "client": client,
            "form": form,
            "feature": feature,
            "data": {"filterFields": filter_fields, "pageInfo": page_info, **extras},
        },
        default=json_default,
    )
    return f"$${json_str}$$"


def _manage_body_params(client_extras, form, feature, filter_fields, page_info, extras):
    if client_extras is None:
        client_extras = {}
    if form is None:
        form = {}
    if feature is None:
        feature = {}
    if filter_fields is None:
        filter_fields = {}
    if page_info is None:
        page_info = {}
    if extras is None:
        extras = {}
    return client_extras, form, feature, filter_fields, page_info, extras


def create_response(db_result=None, form_xml=None, status=None, message=None):
    """Create and return a json response to send to the client"""

    response = {"status": "Failed", "message": {}, "version": {}, "body": {}}

    if status is not None:
        if status in (True, "Accepted"):
            response["status"] = "Accepted"
            if message:
                response["message"] = {"level": 3, "text": message}
        else:
            response["status"] = "Failed"
            if message:
                response["message"] = {"level": 2, "text": message}

        return response

    if not db_result and not form_xml:
        response["status"] = "Failed"
        response["message"] = {"level": 2, "text": "DB returned null"}
        return response
    elif form_xml:
        response["status"] = "Accepted"

    if db_result:
        response = db_result
    response["form_xml"] = form_xml

    return response


async def execute_procedure(  # noqa: C901
    log,
    db_manager,
    function_name,
    parameters=None,
    set_role=True,
    needs_write=False,
    schema=None,
    user: str | None = "anonymous",
    api_version="0.6.0",
):
    """
    Manage execution of database function.

    Args:
        log: Logger instance
        db_manager: DatabaseManager instance from request.app.state.db_manager
        function_name: Name of function to call
        parameters: Parameters for function (json) or (query parameters)
        set_role: Set role in database with the current user
        schema: Database schema to use (defaults to db_manager's default_schema)
        user: Current user (from JWT or config)
        api_version: API version string

    Returns:
        Response of the function executed (json)
    """

    # Manage schema_name and parameters
    schema_name = schema or db_manager.default_schema
    if schema_name is None:
        log.warning(" Schema is None")
        remove_handlers()
        return create_response(status=False, message="Schema not found")

    # Validate schema exists
    if not await db_manager.validate_schema(schema_name):
        log.warning(f"Schema '{schema_name}' not found")
        remove_handlers()
        return create_response(status=False, message=f"Schema '{schema_name}' not found")

    sql = f"SELECT {schema_name}.{function_name}("
    if parameters:
        sql += f"{parameters}"
    sql += ");"

    execution_msg = sql
    response_msg = ""

    start_time = time.monotonic()
    async with db_manager.get_db() as conn:
        if conn is None:
            log.error("No connection to database")
            remove_handlers()
            return create_response(status=False, message="No connection to database")
        result = dict()
        print(f"SERVER EXECUTION: {sql}\n")
        if user == "anonymous":
            identity = None
        else:
            identity = user
        db_error = None
        try:
            async with conn.cursor() as cursor:
                if set_role and identity:
                    await cursor.execute(f"SET ROLE '{identity}';")
                await cursor.execute(sql)
                result = await cursor.fetchone()
                result = result[0] if result else None
                # Manual commit after successful execution
                await conn.commit()
            response_msg = json.dumps(result)
        except Exception as e:
            # Rollback on error
            await conn.rollback()
            db_error = str(e)
            db_version = None
            if result and "version" in result:
                db_version = result["version"]
            result = {
                "status": "Failed",
                "message": {"level": 3, "text": str(e)},
                "version": {"api": api_version},
                "body": {},
            }
            if db_version:
                result["version"]["db"] = db_version
            response_msg = str(e)

        if not result or result.get("status") == "Failed":
            log.warning(f"{execution_msg}|||{response_msg}")
        else:
            log.info(f"{execution_msg}|||{response_msg}")

        if result:
            print(f"SERVER RESPONSE: {json.dumps(result)}\n")

        if result and "version" in result:
            result["version"] = {"db": result["version"], "api": api_version}

        if settings.log_db_enabled:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            request_id = REQUEST_ID_CTX.get()
            db_log_record = {
                "ts": datetime.now(timezone.utc),
                "request_id": request_id,
                "schema_name": schema_name,
                "function_name": function_name,
                "sql_text": sql,
                "response_json": response_msg,
                "duration_ms": duration_ms,
                "status": result.get("status") if isinstance(result, dict) else None,
                "error": db_error,
            }
            asyncio.create_task(insert_api_db_log(db_manager, db_log_record))

        return result


async def execute_sql_select(
    log,
    db_manager,
    table_name: str,
    columns: list[str] | None = None,
    where_clause: str | None = None,
    parameters: tuple | None = None,
    set_role: bool = True,
    schema: str | None = None,
    user: str | None = "anonymous",
):
    """
    Execute a SELECT query on a table and return rows as dicts.
    """
    schema_name = schema or db_manager.default_schema
    if schema_name is None:
        log.warning("Schema is None")
        raise HTTPException(status_code=500, detail="Schema not found")

    if not await db_manager.validate_schema(schema_name):
        log.warning(f"Schema '{schema_name}' not found")
        raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

    if columns:
        column_sql = sql.SQL(", ").join(sql.Identifier(col) for col in columns)
    else:
        column_sql = sql.SQL("*")

    query = sql.SQL("SELECT {} FROM {}.{}").format(column_sql, sql.Identifier(schema_name), sql.Identifier(table_name))
    if where_clause:
        query = sql.SQL("{} WHERE {}").format(query, sql.SQL(where_clause))

    async with db_manager.get_db() as conn:
        if conn is None:
            log.error("No connection to database")
            raise HTTPException(status_code=500, detail="No connection to database")
        try:
            async with conn.cursor(row_factory=dict_row) as cursor:
                identity = None if user == "anonymous" else user
                if set_role and identity:
                    await cursor.execute(sql.SQL("SET ROLE {}").format(sql.Identifier(identity)))
                if parameters is None:
                    await cursor.execute(query)
                else:
                    await cursor.execute(query, parameters)
                rows = await cursor.fetchall()
            await conn.commit()
        except Exception as e:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(e)) from e

    return rows


async def execute_sql(
    log,
    db_manager,
    sql_query: str,
    parameters: tuple | None = None,
    set_role: bool = True,
    schema: str | None = None,
    user: str | None = "anonymous",
):
    """
    Execute a raw SQL query and return rows as dicts.
    Use {schema} in raw_sql for schema-qualified identifiers.
    """
    schema_name = schema or db_manager.default_schema
    if schema_name is None:
        log.warning("Schema is None")
        raise HTTPException(status_code=500, detail="Schema not found")

    if not await db_manager.validate_schema(schema_name):
        log.warning(f"Schema '{schema_name}' not found")
        raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

    try:
        query = sql.SQL(sql_query).format(schema=sql.Identifier(schema_name))  # type: ignore
    except Exception as e:
        log.error(f"Failed to create SQL query: {e}")
        raise HTTPException(status_code=500, detail=f"Invalid SQL query or parameters: {e}") from e

    async with db_manager.get_db() as conn:
        if conn is None:
            log.error("No connection to database")
            raise HTTPException(status_code=500, detail="No connection to database")
        try:
            async with conn.cursor(row_factory=dict_row) as cursor:
                identity = None if user == "anonymous" else user
                if set_role and identity:
                    await cursor.execute(sql.SQL("SET ROLE {}").format(sql.Identifier(identity)))
                if parameters is None:
                    await cursor.execute(query)
                else:
                    await cursor.execute(query, parameters)
                rows = await cursor.fetchall()
            await conn.commit()
        except Exception as e:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(e)) from e

    return rows


async def get_db_version(log, db_manager, schema: str | None = None) -> str | None:
    """
    Return latest giswater version from sys_version.
    """
    schema_name = schema or db_manager.default_schema
    if schema_name is None:
        log.warning("Schema is None")
        raise HTTPException(status_code=500, detail="Schema not found")

    if not await db_manager.validate_schema(schema_name):
        log.warning(f"Schema '{schema_name}' not found")
        raise HTTPException(status_code=404, detail=f"Schema '{schema_name}' not found")

    query = sql.SQL("SELECT giswater FROM {}.sys_version ORDER BY id DESC LIMIT 1").format(sql.Identifier(schema_name))
    async with db_manager.get_db() as conn:
        if conn is None:
            log.error("No connection to database")
            raise HTTPException(status_code=500, detail="No connection to database")
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                row = await cursor.fetchone()
            await conn.commit()
        except Exception as e:
            await conn.rollback()
            raise HTTPException(status_code=500, detail=str(e)) from e

    if not row:
        return None
    return row[0]


# Create log pointer
def create_log(class_name):
    today = date.today()
    today = today.strftime("%Y%m%d")

    # Directory where log file is saved, changes location depending on what tenant is used
    # logs_directory = "/var/log/giswater-api-server"
    logs_directory = settings.log_dir
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)

    # Check if today's direcotry is created
    today_directory = f"{logs_directory}/{today}"
    if not os.path.exists(today_directory):
        # This shouldn't be necessary, but somehow the directory magically apears
        # (only the first time of the day it is created)
        try:
            os.makedirs(today_directory)
        except FileExistsError:
            print("Directory already exists. wtf")

    service_name = os.getcwd().split(os.sep)[-1]
    # Select file name for the log
    log_file = f"{service_name}_{today}.log"

    log_path = os.path.join(today_directory, log_file)
    if not os.path.exists(log_path):
        open(log_path, "a", encoding="utf-8").close()

    fileh = TimedRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=settings.log_rotate_days,
        encoding="utf-8",
        utc=False,
    )
    # Declares how log info is added to the file
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s", datefmt="%d/%m/%y %H:%M:%S")
    fileh.setFormatter(formatter)

    # Removes previous handlers on root Logger
    # Gets root Logger and add handler
    logger_name = f"{class_name.split('.')[-1]}"
    log = logging.getLogger(logger_name)
    remove_handlers(log)
    log.addHandler(fileh)
    log.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    return log


# Removes previous handlers on root Logger
def remove_handlers(log=None):
    if log is None:
        log = logging.getLogger()
    for hdlr in log.handlers[:]:
        log.removeHandler(hdlr)


LOG_SCHEMA = "log"
LOG_TABLE = "gw_api_logs"
LOG_DB_TABLE = "gw_api_logs_db"
REQUEST_ID_CTX: contextvars.ContextVar[uuid.UUID | None] = contextvars.ContextVar("request_id", default=None)


async def ensure_log_schema(db_manager) -> None:
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(LOG_SCHEMA)))
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            ts timestamptz NOT NULL,
                            id bigserial NOT NULL,
                            method text NOT NULL,
                            endpoint text NOT NULL,
                            status integer NOT NULL,
                            duration_ms integer,
                            user_name text,
                            request_id uuid,
                            client_ip inet,
                            query_params jsonb,
                            body_size integer,
                            response_size integer,
                            request_headers jsonb,
                            request_body text,
                            response_headers jsonb,
                            response_body text,
                            PRIMARY KEY (ts, id)
                        ) PARTITION BY RANGE (ts)
                        """
                    ).format(sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE))
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS request_headers jsonb").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS request_body text").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS response_headers jsonb").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} ADD COLUMN IF NOT EXISTS response_body text").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("ALTER TABLE {}.{} DROP COLUMN IF EXISTS user_agent").format(
                        sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (ts DESC)").format(
                        sql.Identifier("gw_api_logs_ts_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (endpoint)").format(
                        sql.Identifier("gw_api_logs_endpoint_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (method)").format(
                        sql.Identifier("gw_api_logs_method_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (status)").format(
                        sql.Identifier("gw_api_logs_status_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (user_name)").format(
                        sql.Identifier("gw_api_logs_user_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (request_id)").format(
                        sql.Identifier("gw_api_logs_request_id_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {}.{} (
                            ts timestamptz NOT NULL,
                            id bigserial NOT NULL,
                            request_id uuid,
                            schema_name text,
                            function_name text,
                            sql_text text,
                            response_json text,
                            duration_ms integer,
                            status text,
                            error text,
                            PRIMARY KEY (ts, id)
                        ) PARTITION BY RANGE (ts)
                        """
                    ).format(sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_DB_TABLE))
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (ts DESC)").format(
                        sql.Identifier("gw_api_logs_db_ts_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_DB_TABLE),
                    )
                )
                await cursor.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {}.{} (request_id)").format(
                        sql.Identifier("gw_api_logs_db_request_id_idx"),
                        sql.Identifier(LOG_SCHEMA),
                        sql.Identifier(LOG_DB_TABLE),
                    )
                )
            await conn.commit()
            await ensure_log_partition(conn, datetime.now(timezone.utc), LOG_TABLE)
            await ensure_log_partition(conn, datetime.now(timezone.utc), LOG_DB_TABLE)
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise


def _month_range(ts: datetime, table_name: str) -> tuple[datetime, datetime, str]:
    month_start = datetime(ts.year, ts.month, 1, tzinfo=ts.tzinfo)
    if ts.month == 12:
        month_end = datetime(ts.year + 1, 1, 1, tzinfo=ts.tzinfo)
    else:
        month_end = datetime(ts.year, ts.month + 1, 1, tzinfo=ts.tzinfo)
    partition_name = f"{table_name}_{month_start.year}_{month_start.month:02d}"
    return month_start, month_end, partition_name


async def ensure_log_partition(conn, ts: datetime, table_name: str) -> None:
    month_start, month_end, partition_name = _month_range(ts, table_name)
    async with conn.cursor() as cursor:
        await cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.{}
                PARTITION OF {}.{}
                FOR VALUES FROM ({}) TO ({})
                """
            ).format(
                sql.Identifier(LOG_SCHEMA),
                sql.Identifier(partition_name),
                sql.Identifier(LOG_SCHEMA),
                sql.Identifier(table_name),
                sql.Literal(month_start),
                sql.Literal(month_end),
            ),
        )


async def insert_api_log(db_manager, record: Dict[str, Any]) -> None:
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            await ensure_log_partition(conn, record["ts"], LOG_TABLE)
            async with conn.cursor() as cursor:
                await cursor.execute(
                    sql.SQL(
                        """
                        INSERT INTO {}.{} (
                            ts,
                            method,
                            endpoint,
                            status,
                            duration_ms,
                            user_name,
                            request_id,
                            client_ip,
                            query_params,
                            body_size,
                            response_size,
                            request_headers,
                            request_body,
                            response_headers,
                            response_body
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                    ).format(sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_TABLE)),
                    (
                        record.get("ts"),
                        record.get("method"),
                        record.get("endpoint"),
                        record.get("status"),
                        record.get("duration_ms"),
                        record.get("user_name"),
                        record.get("request_id"),
                        record.get("client_ip"),
                        Json(record.get("query_params")) if record.get("query_params") is not None else None,
                        record.get("body_size"),
                        record.get("response_size"),
                        Json(record.get("request_headers")) if record.get("request_headers") is not None else None,
                        record.get("request_body"),
                        Json(record.get("response_headers")) if record.get("response_headers") is not None else None,
                        record.get("response_body"),
                    ),
                )
            await conn.commit()
        except Exception:
            await conn.rollback()


async def insert_api_db_log(db_manager, record: Dict[str, Any]) -> None:
    async with db_manager.get_db() as conn:
        if conn is None:
            return
        try:
            await ensure_log_partition(conn, record["ts"], LOG_DB_TABLE)
            async with conn.cursor() as cursor:
                await cursor.execute(
                    sql.SQL(
                        """
                        INSERT INTO {}.{} (
                            ts,
                            request_id,
                            schema_name,
                            function_name,
                            sql_text,
                            response_json,
                            duration_ms,
                            status,
                            error
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                    ).format(sql.Identifier(LOG_SCHEMA), sql.Identifier(LOG_DB_TABLE)),
                    (
                        record.get("ts"),
                        record.get("request_id"),
                        record.get("schema_name"),
                        record.get("function_name"),
                        record.get("sql_text"),
                        record.get("response_json"),
                        record.get("duration_ms"),
                        record.get("status"),
                        record.get("error"),
                    ),
                )
            await conn.commit()
        except Exception:
            await conn.rollback()


def create_api_response(
    message: str, status: Literal["Accepted", "Failed"], result: Dict[str, Any] | Any | None = None
) -> APIResponse:
    """
    Creates a standardized API response.

    Args:
        message: Response message
        status: Response status ("Accepted" or "Failed")
        result: Optional result data to include in the response

    Returns:
        APIResponse containing the standardized response
    """
    return APIResponse(message=message, status=status, result=result)


def handle_procedure_result(result: dict | None) -> dict:
    """
    Validate procedure result and raise appropriate exception on error.

    Args:
        result: Result from execute_procedure

    Returns:
        The result dict if valid

    Raises:
        HTTPException: If result is None
        ProcedureError: If result status is not "Accepted"
    """
    if not result:
        raise HTTPException(status_code=500, detail="Database returned null")
    if result.get("status") != "Accepted":
        raise ProcedureError(result)
    return result
