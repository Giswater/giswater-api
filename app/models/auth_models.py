"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

AuthMethod = Literal["none", "keycloak", "basic"]


@dataclass(frozen=True)
class ApiUser:
    """Unified tenant API identity for all auth modes."""

    sub: str
    preferred_username: str
    auth_method: AuthMethod
    roles: frozenset[str] = frozenset()
    db_role: str | None = None

    @property
    def is_anonymous(self) -> bool:
        return self.auth_method == "none"

    def has_role(self, *names: str) -> bool:
        return any(role in self.roles for role in names)

    def has_any_role(self, names: Iterable[str]) -> bool:
        return bool(self.roles.intersection(names))

    @classmethod
    def anonymous(cls) -> "ApiUser":
        return cls(
            sub="anonymous",
            preferred_username="anonymous",
            auth_method="none",
        )
