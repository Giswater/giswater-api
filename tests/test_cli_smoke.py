"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import json

from click.testing import CliRunner

from app.cli.main import main


def test_cli_admin_tenants_list():
    runner = CliRunner()
    result = runner.invoke(main, ["admin", "tenants", "list"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert isinstance(payload, list)
