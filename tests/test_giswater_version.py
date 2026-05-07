"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import pytest

from app.giswater_version import db_version_at_least, version_tuple_from_string


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("4.8.0", "4.8.0", True),
        ("4.9.1", "4.8.0", True),
        ("4.7.9", "4.8.0", False),
        ("4.10.0", "4.8.0", True),
        ("v4.8.1-beta", "4.8.0", True),
    ],
)
def test_db_version_at_least(left: str, right: str, expected: bool) -> None:
    assert db_version_at_least(left, right) is expected


def test_version_tuple_from_string() -> None:
    assert version_tuple_from_string("4.8.12") == (4, 8, 12)
    assert version_tuple_from_string("") == ()
