"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import json
import os

from click.testing import CliRunner

from app.cli.main import main


def test_cli_lists_materialized_test_tenant():
    """CLI loads the same tenants dir as the HTTP test suite and exits cleanly."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--tenants-dir", os.environ["TENANTS_DIR"], "admin", "tenants", "list"],
    )

    assert result.exit_code == 0, result.output
    tenants = json.loads(result.output)
    assert any(t["id"] == "test" for t in tenants)
