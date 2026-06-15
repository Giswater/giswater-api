"""
Loose version comparison for Giswater DB `sys_version.giswater` strings (e.g. "4.8.1", "4.8").
"""

import re
from typing import Final

_TOKEN_RE: Final = re.compile(r"(\d+)")


def version_tuple_from_string(s: str) -> tuple[int, ...]:
    """Extract leading integer components; non-numeric parts are ignored."""
    if not s or not str(s).strip():
        return ()
    parts: list[int] = []
    for m in _TOKEN_RE.finditer(str(s)):
        try:
            parts.append(int(m.group(1)))
        except ValueError:
            break
    return tuple(parts)


def db_version_at_least(db_version: str | None, minimum: str) -> bool:
    """True if `db_version` is >= `minimum` using tuple comparison (padded with zeros)."""
    if not db_version:
        return False
    left = version_tuple_from_string(db_version)
    right = version_tuple_from_string(minimum)
    if not left or not right:
        return False
    maxlen = max(len(left), len(right))
    left_pad = left + (0,) * (maxlen - len(left))
    right_pad = right + (0,) * (maxlen - len(right))
    return left_pad >= right_pad
