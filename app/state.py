"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

from .tenant import TenantRegistry

registry: TenantRegistry | None = None
global_logger: logging.Logger | None = None
