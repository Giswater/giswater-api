"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging
import os

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def load_plugins(app: FastAPI):
    """
    Load plugins from the plugins directory for a specific app instance.

    Args:
        app: FastAPI app instance to register plugins to
    """
    from importlib import import_module

    plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "plugins"))
    if not os.path.exists(plugins_dir):
        return

    # Do not block API startup when plugin directory exists but is not accessible.
    try:
        plugin_entries = os.listdir(plugins_dir)
    except PermissionError as e:
        logging.warning("Skipping plugin loading: cannot read '%s' (%s)", plugins_dir, e)
        return

    for plugin in plugin_entries:
        if not os.path.isdir(f"{plugins_dir}/{plugin}"):
            continue

        try:
            module = import_module(f"plugins.{plugin}")
            module.register_plugin(app)
        except Exception:
            logger.exception("Failed to load plugin '%s'", plugin)
