"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

# API surface prefixes (part of the public contract; not configurable at runtime).
# All surface paths live under API_ROOT so they cannot clash with other apps on the same host.
API_ROOT = "/gw-api"
TENANT_PREFIX = f"{API_ROOT}/v1"
ADMIN_PREFIX = f"{API_ROOT}/admin"
GLOBAL_HEALTH_PATH = f"{API_ROOT}/health"
STATIC_PREFIX = f"{API_ROOT}/static"
