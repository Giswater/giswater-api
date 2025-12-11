"""
Keycloak configuration - import get_current_user from here in routes.
"""
import os
from fastapi_keycloak import FastAPIKeycloak, OIDCUser
from .config import Config

# Load config
config_path = os.environ.get("CONFIG_PATH", "app/config/app.config")
config = Config(config_path)

# Initialize Keycloak
idp = None
if config.get_bool("keycloak", "enabled"):
    realm = config.get_str("keycloak", "realm")
    url = config.get_str("keycloak", "url")
    client_id = config.get_str("keycloak", "client_id")
    client_secret = config.get_str("keycloak", "client_secret")
    admin_client_secret = config.get_str("keycloak", "admin_client_secret")
    callback_uri = config.get_str("keycloak", "callback_uri")
    if not realm or not url or not client_id or not client_secret or not admin_client_secret or not callback_uri:
        raise ValueError("Keycloak configuration is incomplete")

    idp = FastAPIKeycloak(
        server_url=url,
        client_id=client_id,
        client_secret=client_secret,
        admin_client_secret=admin_client_secret,
        realm=realm,
        callback_uri=callback_uri
    )


# Dependency for routes - works with or without Keycloak
def get_current_user():
    """
    Returns a dependency for getting the current user.
    When Keycloak is enabled, validates token and returns OIDCUser.
    When disabled, returns anonymous user.
    """
    if idp:
        return idp.get_current_user()

    # Keycloak disabled - return anonymous user dependency
    async def anonymous_user() -> OIDCUser:
        return OIDCUser(
            sub="anonymous",
            iat=0,
            exp=0,
            email=None,
            email_verified=False,
            preferred_username="anonymous"
        )
    return anonymous_user
