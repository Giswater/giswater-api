"""
Copyright © 2024 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

import os
import logging
import json

from typing import Any, Dict, Literal
from datetime import date, datetime
from fastapi import FastAPI

from ..models.util_models import APIResponse


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
    client_extras={},
    form={},
    feature={},
    filter_fields={},
    pageInfo={},
    extras={},
    cur_user: str | None = "anonymous",
    device: int = 4,
    lang: str = "es_ES"
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
    if cur_user == 'anonymous':
        cur_user = None

    client = {
        "device": device,
        "lang": lang,
        "cur_user": cur_user,
        **client_extras
    }
    if info_type is not None:
        client["infoType"] = info_type
    if project_epsg is not None:
        client["epsg"] = project_epsg

    def json_default(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    json_str = json.dumps({
        "client": client,
        "form": form,
        "feature": feature,
        "data": {
            "filterFields": filter_fields,
            "pageInfo": pageInfo,
            **extras
        }
    }, default=json_default)
    return f"$${json_str}$$"


def create_response(db_result=None, form_xml=None, status=None, message=None):
    """ Create and return a json response to send to the client """

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


def execute_procedure(
    log,
    db_manager,
    function_name,
    parameters=None,
    set_role=True,
    needs_write=False,
    schema=None,
    user: str | None = "anonymous",
    api_version="0.4.0"
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
    if not db_manager.validate_schema(schema_name):
        log.warning(f"Schema '{schema_name}' not found")
        remove_handlers()
        return create_response(status=False, message=f"Schema '{schema_name}' not found")

    sql = f"SELECT {schema_name}.{function_name}("
    if parameters:
        sql += f"{parameters}"
    sql += ");"

    execution_msg = sql
    response_msg = ""

    with db_manager.get_db() as conn:
        if conn is None:
            log.error("No connection to database")
            remove_handlers()
            return create_response(status=False, message="No connection to database")
        result = dict()
        print(f"SERVER EXECUTION: {sql}\n")
        if user == 'anonymous':
            identity = None
        else:
            identity = user
        try:
            with conn.cursor() as cursor:
                if set_role and identity:
                    cursor.execute(f"SET ROLE '{identity}';")
                cursor.execute(sql)
                result = cursor.fetchone()
                result = result[0] if result else None
                # Manual commit after successful execution
                conn.commit()
            response_msg = json.dumps(result)
        except Exception as e:
            # Rollback on error
            conn.rollback()
            db_version = None
            if result and 'version' in result:
                db_version = result['version']
            result = {
                "status": "Failed",
                "message": {"level": 3, "text": str(e)},
                "version": {"api": api_version},
                "body": {}
            }
            if db_version:
                result["version"]["db"] = db_version
            response_msg = str(e)

        if not result or result.get('status') == "Failed":
            log.warning(f"{execution_msg}|||{response_msg}")
        else:
            log.info(f"{execution_msg}|||{response_msg}")

        if result:
            print(f"SERVER RESPONSE: {json.dumps(result)}\n")

        if result and "version" in result:
            result["version"] = {"db": result['version'], "api": api_version}

        return result


# Create log pointer
def create_log(class_name):
    today = date.today()
    today = today.strftime("%Y%m%d")

    # Directory where log file is saved, changes location depending on what tenant is used
    # logs_directory = "/var/log/giswater-api-server"
    logs_directory = "logs"
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

    fileh = logging.FileHandler(f"{today_directory}/{log_file}", "a", encoding="utf-8")
    # Declares how log info is added to the file
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s", datefmt="%d/%m/%y %H:%M:%S")
    fileh.setFormatter(formatter)

    # Removes previous handlers on root Logger
    remove_handlers()
    # Gets root Logger and add handler
    logger_name = f"{class_name.split('.')[-1]}"
    log = logging.getLogger(logger_name)
    # log = logging.getLogger()
    log.addHandler(fileh)
    log.setLevel(logging.DEBUG)
    return log


# Removes previous handlers on root Logger
def remove_handlers(log=logging.getLogger()):
    for hdlr in log.handlers[:]:
        log.removeHandler(hdlr)


def create_api_response(
    message: str,
    status: Literal["Accepted", "Failed"],
    result: Dict[str, Any] | Any | None = None
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
    return APIResponse(
        message=message,
        status=status,
        result=result
    )
