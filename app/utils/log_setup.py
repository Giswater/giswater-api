"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging
import os
from datetime import date
from logging.handlers import TimedRotatingFileHandler

from ..core.config import global_settings

logger = logging.getLogger(__name__)


# Create log pointer
def create_log(class_name: str, log_dir: str | None = None):
    """Build a `TimedRotatingFileHandler`-backed logger.

    `log_dir` is the *base* directory; today's date is appended automatically
    so daily rotation lands in `<log_dir>/<YYYYMMDD>/`. When omitted, falls
    back to `global_settings.log_dir` for legacy callers (transitional)."""
    today = date.today().strftime("%Y%m%d")

    logs_directory = log_dir or global_settings.log_dir

    logger_name = f"{class_name.split('.')[-1]}"
    log = logging.getLogger(logger_name)
    remove_handlers(log)

    def _fallback_stream_logger(reason: Exception):
        logger.warning("File logging disabled (%s). Falling back to stdout logging.", reason)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s", datefmt="%d/%m/%y %H:%M:%S")
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)
        log.setLevel(getattr(logging, global_settings.log_level.upper(), logging.INFO))
        return log

    try:
        if not os.path.exists(logs_directory):
            os.makedirs(logs_directory, exist_ok=True)

        today_directory = os.path.join(logs_directory, today)
        os.makedirs(today_directory, exist_ok=True)

        service_name = os.getcwd().split(os.sep)[-1]
        log_file = f"{service_name}_{today}.log"

        log_path = os.path.join(today_directory, log_file)
        if not os.path.exists(log_path):
            open(log_path, "a", encoding="utf-8").close()

        fileh = TimedRotatingFileHandler(
            log_path,
            when="midnight",
            interval=1,
            backupCount=global_settings.log_rotate_days,
            encoding="utf-8",
            utc=False,
        )
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s", datefmt="%d/%m/%y %H:%M:%S")
        fileh.setFormatter(formatter)
    except OSError as e:
        return _fallback_stream_logger(e)

    log.addHandler(fileh)
    log.setLevel(getattr(logging, global_settings.log_level.upper(), logging.INFO))
    return log


# Removes previous handlers on root Logger
def remove_handlers(log=None):
    if log is None:
        log = logging.getLogger()
    for hdlr in log.handlers[:]:
        log.removeHandler(hdlr)
