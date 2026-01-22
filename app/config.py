"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("true", "t", "yes", "y", "1", "on")


@dataclass(frozen=True)
class Settings:
    # API toggles
    api_basic: bool = _get_bool("API_BASIC", True)
    api_profile: bool = _get_bool("API_PROFILE", True)
    api_flow: bool = _get_bool("API_FLOW", True)
    api_mincut: bool = _get_bool("API_MINCUT", True)
    api_water_balance: bool = _get_bool("API_WATER_BALANCE", True)
    api_routing: bool = _get_bool("API_ROUTING", True)
    api_crm: bool = _get_bool("API_CRM", True)

    # Database
    db_host: str | None = _get_env("DB_HOST", "localhost")
    db_port: str | None = _get_env("DB_PORT", "5432")
    db_name: str | None = _get_env("DB_NAME", "postgres")
    db_user: str | None = _get_env("DB_USER", "postgres")
    db_password: str | None = _get_env("DB_PASSWORD", "postgres")
    db_schema: str | None = _get_env("DB_SCHEMA", "public")
    database_url: str | None = _get_env("DATABASE_URL")

    # Hydraulic engine
    hydraulic_engine_enabled: bool = _get_bool("HYDRAULIC_ENGINE_ENABLED", True)
    hydraulic_engine_ws: bool = _get_bool("HYDRAULIC_ENGINE_WS", True)
    hydraulic_engine_ud: bool = _get_bool("HYDRAULIC_ENGINE_UD", True)
    hydraulic_engine_url: str | None = _get_env("HYDRAULIC_ENGINE_URL")

    # Keycloak
    keycloak_enabled: bool = _get_bool("KEYCLOAK_ENABLED", False)
    keycloak_url: str | None = _get_env("KEYCLOAK_URL")
    keycloak_realm: str | None = _get_env("KEYCLOAK_REALM")
    keycloak_client_id: str | None = _get_env("KEYCLOAK_CLIENT_ID")
    keycloak_client_secret: str | None = _get_env("KEYCLOAK_CLIENT_SECRET")
    keycloak_admin_client_secret: str | None = _get_env("KEYCLOAK_ADMIN_CLIENT_SECRET")
    keycloak_callback_uri: str | None = _get_env("KEYCLOAK_CALLBACK_URI")

    def validate(self) -> None:
        if self.keycloak_enabled:
            missing = [
                name
                for name, value in (
                    ("KEYCLOAK_URL", self.keycloak_url),
                    ("KEYCLOAK_REALM", self.keycloak_realm),
                    ("KEYCLOAK_CLIENT_ID", self.keycloak_client_id),
                    ("KEYCLOAK_CLIENT_SECRET", self.keycloak_client_secret),
                    ("KEYCLOAK_ADMIN_CLIENT_SECRET", self.keycloak_admin_client_secret),
                    ("KEYCLOAK_CALLBACK_URI", self.keycloak_callback_uri),
                )
                if not value
            ]
            if missing:
                raise ValueError(f"Keycloak configuration is incomplete: {', '.join(missing)}")


settings = Settings()
settings.validate()
