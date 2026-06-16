"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

import json
import logging
from typing import Literal, Optional

import requests
from pydantic import ValidationError

from app.schemas.routing.routing_models import Location, OptimalPathParams
from app.services.context import ServiceContext
from app.services.procedure import run_procedure
from app.utils.body import create_body_dict
from app.utils.routing import (
    get_geojson_from_optimized_route,
    get_maneuvers,
    get_network_points,
    get_valhalla_optimized_route,
)


class RoutingService:
    def __init__(self, ctx: ServiceContext):
        self.ctx = ctx.with_logger(__name__)

    async def get_object_optimal_path_order(
        self,
        object_type: str,
        mapzone_type: Literal["EXPLOITATION", "SECTOR"],
        mapzone_id: int,
        initial_point: str,
        final_point: Optional[str],
        transport_mode: Literal["auto", "pedestrian", "bicycle"],
        units: Literal["miles", "kilometers"],
        language: str,
    ) -> dict:
        try:
            final_point_value = initial_point if final_point is None else final_point
            initial_point_data = json.loads(initial_point)
            final_point_data = json.loads(final_point_value)
            initial = Location(**initial_point_data)
            final = Location(**final_point_data)

            mapzone_type_value = "EXPL" if mapzone_type == "EXPLOITATION" else mapzone_type

            json_result, network_points = await get_network_points(
                object_type,
                mapzone_type_value,
                mapzone_id,
                self.ctx.logger,
                self.ctx.db_manager,
                self.ctx.schema,
                api_version=self.ctx.api_version,
            )
            features = json_result["body"]["data"]["features"]
            locations_data = [initial, *network_points, final]
            params = OptimalPathParams(locations=locations_data, costing=transport_mode, units=units)
            valhalla_params = {
                "locations": [location.to_dict() for location in locations_data],
                "costing": params.costing,
                "units": params.units,
                "language": language,
            }
            valhalla_response, _legs = get_valhalla_optimized_route(valhalla_params)
            logging.getLogger(__name__).debug(
                "Valhalla optimized_route response: %s", json.dumps(valhalla_response, default=str)
            )
            if not isinstance(valhalla_response, dict):
                raise RuntimeError("Invalid response from Valhalla API")
            try:
                geojson_response = get_geojson_from_optimized_route(valhalla_response.get("trip", {}), params.costing)
            except (KeyError, TypeError, ValueError):
                logging.getLogger(__name__).warning("Error creating GeoJSON from optimized route", exc_info=True)
                geojson_response = {}
            trip = valhalla_response.get("trip") or {}
            summary = trip.get("summary") or {}
            try:
                maneuvers = get_maneuvers(valhalla_response)
            except (KeyError, TypeError, IndexError):
                maneuvers = []
            version = (json_result.get("version") or {}) if isinstance(json_result, dict) else {}
            version["api"] = self.ctx.api_version
            return {
                "status": "Accepted",
                "message": {"level": 1, "text": trip.get("status_message")},
                "version": version,
                "body": {
                    "data": {
                        "distance": summary.get("length"),
                        "duration": summary.get("time"),
                        "path": geojson_response,
                        "maneuvers": maneuvers,
                        "features": features,
                    }
                },
            }
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON format for initialPoint or finalPoint parameter") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"Routing provider unavailable: {exc}") from exc
        except ValidationError as exc:
            raise ValueError(str(exc)) from exc

    async def get_object_parameter_order(
        self,
        object_type: str,
        mapzone_type: Literal["EXPLOITATION", "SECTOR"],
        mapzone_id: int,
        parameter: str,
        order: Literal["asc", "desc"],
    ) -> dict:
        mapzone_type_value = "EXPL" if mapzone_type == "EXPLOITATION" else mapzone_type
        body = create_body_dict(
            device=self.ctx.device,
            extras={
                "sysType": object_type,
                "mapzoneType": mapzone_type_value,
                "mapzoneId": mapzone_id,
                "parameter": parameter,
                "order": order,
            },
            cur_user=self.ctx.user_id,
        )
        return await run_procedure(self.ctx, "gw_fct_getfeatures", body)
