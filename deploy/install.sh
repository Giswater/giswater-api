#!/usr/bin/env bash
# Interactive production installer for Giswater API (single-tenant mode).
#
# Usage (from any directory):
#   curl -fsSL https://raw.githubusercontent.com/Giswater/giswater-api/main/deploy/install.sh | sudo bash
#
# Or download and run:
#   wget -O install.sh https://raw.githubusercontent.com/Giswater/giswater-api/main/deploy/install.sh
#   chmod +x install.sh && sudo ./install.sh
#
# Pin deploy templates to a release (docker-compose.yml, entrypoint, env examples):
#   GISWATER_API_REF=v1.3.2 curl -fsSL .../deploy/install.sh | sudo bash
#
# Environment overrides (optional):
#   GISWATER_API_INSTALL_DIR   default /opt/giswater-api
#   GISWATER_API_REF           git ref for deploy assets (default main)
#   GISWATER_API_IMAGE         Docker image (default bgeoopengis/giswater-api)
#   GISWATER_API_TAG           default for the image-tag prompt (default latest)

set -euo pipefail

REPO="${GISWATER_API_REPO:-Giswater/giswater-api}"
REF="${GISWATER_API_REF:-main}"
INSTALL_DIR="${GISWATER_API_INSTALL_DIR:-/opt/giswater-api}"
DEFAULT_IMAGE="${GISWATER_API_IMAGE:-bgeoopengis/giswater-api}"
DEFAULT_TAG="${GISWATER_API_TAG:-latest}"
TENANT_ID="${GISWATER_API_TENANT_ID:-main}"
API_ROOT="${GISWATER_API_ROOT:-/giswater}"

RAW_BASE="https://raw.githubusercontent.com/${REPO}/${REF}/deploy"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { printf "${GREEN}==>${NC} %s\n" "$*"; }
warn() { printf "${YELLOW}==>${NC} %s\n" "$*"; }
err()  { printf "${RED}ERROR:${NC} %s\n" "$*" >&2; }

prompt() {
  local var_name="$1"
  local question="$2"
  local default="${3:-}"
  local value=""
  if [[ -n "$default" ]]; then
    read -r -p "${question} [${default}]: " value </dev/tty
    value="${value:-$default}"
  else
    read -r -p "${question}: " value </dev/tty
  fi
  printf -v "$var_name" '%s' "$value"
}

prompt_secret() {
  local var_name="$1"
  local question="$2"
  local value=""
  read -r -s -p "${question}: " value </dev/tty
  echo
  printf -v "$var_name" '%s' "$value"
}

prompt_yes_no() {
  local var_name="$1"
  local question="$2"
  local default="${3:-n}"
  local value=""
  local hint="y/N"
  [[ "${default,,}" == "y" || "${default,,}" == "yes" ]] && hint="Y/n"
  read -r -p "${question} [${hint}]: " value </dev/tty
  value="${value:-$default}"
  case "${value,,}" in
    y|yes) printf -v "$var_name" '%s' "true" ;;
    *) printf -v "$var_name" '%s' "false" ;;
  esac
}

require_root() {
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    err "Run as root (e.g. curl ... | sudo bash)."
    exit 1
  fi
}

require_commands() {
  local missing=()
  for cmd in curl docker; do
    command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    err "Missing required commands: ${missing[*]}"
    exit 1
  fi
  if ! docker compose version >/dev/null 2>&1; then
    err "Docker Compose plugin not found (install docker-compose-plugin)."
    exit 1
  fi
}

download_file() {
  local remote="$1"
  local dest="$2"
  curl -fsSL "${RAW_BASE}/${remote}" -o "$dest"
}

escape_sed_replacement() {
  printf '%s' "$1" | sed -e 's/[&|\\|]/\\&/g'
}

set_env_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  local escaped
  escaped="$(escape_sed_replacement "$value")"
  if grep -q "^${key}=" "$file"; then
    sed -i "s|^${key}=.*|${key}=${escaped}|" "$file"
  else
    printf '%s=%s\n' "$key" "$value" >>"$file"
  fi
}

generate_admin_password() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 24
  else
    tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24
  fi
}

normalize_public_url() {
  local url="$1"
  url="${url%/}"
  if [[ ! "$url" =~ ^https?:// ]]; then
    url="http://${url}"
  fi
  printf '%s' "$url"
}

# .env is read by Docker Compose on the host (600). Tenant env files are read
# inside the container by the non-root app user, so they must be world-readable
# (config is bind-mounted read-only — the entrypoint cannot fix this).
fix_permissions() {
  local dir="$1"
  chmod 600 "${dir}/.env"
  chmod 755 "${dir}/config" "${dir}/config/tenants"
  chmod 644 "${dir}/config/tenants/"*.env 2>/dev/null || true
}

main() {
  require_root
  require_commands

  echo
  info "Giswater API production installer (single-tenant: ${TENANT_ID})"
  info "Deploy assets: ${RAW_BASE}/"
  echo

  if [[ -d "$INSTALL_DIR" ]] && [[ -n "$(ls -A "$INSTALL_DIR" 2>/dev/null || true)" ]]; then
    warn "Install directory already exists: ${INSTALL_DIR}"
    prompt_yes_no REINSTALL "Overwrite existing configuration and redeploy" "n"
    if [[ "$REINSTALL" != "true" ]]; then
      info "Aborted."
      exit 0
    fi
  fi

  # --- Interactive configuration ---
  local public_url=""
  local image_tag=""
  local admin_password=""
  local db_host=""
  local db_port=""
  local db_name=""
  local db_user=""
  local db_password=""
  local db_schema=""
  local keycloak_enabled=""
  local keycloak_url=""
  local keycloak_realm=""
  local keycloak_client_id=""
  local keycloak_client_secret=""
  local keycloak_callback=""

  prompt public_url "Public URL or server IP (used for Keycloak callback hints)" "http://127.0.0.1"
  public_url="$(normalize_public_url "$public_url")"

  prompt image_tag "Docker image tag" "$DEFAULT_TAG"

  prompt_secret admin_password "Admin API password (leave empty to auto-generate)"
  if [[ -z "$admin_password" ]]; then
    admin_password="$(generate_admin_password)"
    info "Generated ADMIN_PASSWORD: ${admin_password}"
  fi

  echo
  info "Database (Postgres with Giswater schema)"
  prompt db_host "DB host (use host.docker.internal when Postgres runs on this server)" "host.docker.internal"
  prompt db_port "DB port" "5432"
  prompt db_name "DB name" "postgres"
  prompt db_user "DB user" "postgres"
  prompt_secret db_password "DB password"
  prompt db_schema "Giswater schema (e.g. ws_40 or ud_40)" "ws_40"

  echo
  prompt_yes_no keycloak_enabled "Enable Keycloak for tenant API" "n"
  if [[ "$keycloak_enabled" == "true" ]]; then
    prompt keycloak_url "Keycloak base URL (e.g. https://auth.example.com)" ""
    prompt keycloak_realm "Keycloak realm" ""
    prompt keycloak_client_id "Keycloak client ID" "giswater-api"
    prompt_secret keycloak_client_secret "Keycloak client secret"
    local default_callback="${public_url}${API_ROOT}/v1/auth/callback"
    prompt keycloak_callback "Keycloak callback URI" "$default_callback"
  else
    keycloak_url=""
    keycloak_realm=""
    keycloak_client_id=""
    keycloak_client_secret=""
    keycloak_callback=""
  fi

  echo
  prompt_yes_no START_NOW "Pull image and start containers now" "y"

  # --- Layout ---
  info "Creating ${INSTALL_DIR}"
  mkdir -p "${INSTALL_DIR}/config/tenants"

  info "Downloading deploy files (ref: ${REF})"
  download_file "docker-compose.yml" "${INSTALL_DIR}/docker-compose.yml"
  download_file "docker-entrypoint.sh" "${INSTALL_DIR}/docker-entrypoint.sh"
  download_file ".env.prod.example" "${INSTALL_DIR}/.env"
  download_file "main.env.example" "${INSTALL_DIR}/config/tenants/${TENANT_ID}.env"

  chmod 755 "${INSTALL_DIR}/docker-entrypoint.sh"

  # --- .env ---
  set_env_value "${INSTALL_DIR}/.env" "GISWATER_API_IMAGE" "$DEFAULT_IMAGE"
  set_env_value "${INSTALL_DIR}/.env" "GISWATER_API_TAG" "$image_tag"
  set_env_value "${INSTALL_DIR}/.env" "SINGLE_TENANT_ID" "$TENANT_ID"
  set_env_value "${INSTALL_DIR}/.env" "API_ROOT" "$API_ROOT"
  set_env_value "${INSTALL_DIR}/.env" "ADMIN_PASSWORD" "$admin_password"

  # --- tenant env ---
  local tenant_file="${INSTALL_DIR}/config/tenants/${TENANT_ID}.env"
  set_env_value "$tenant_file" "DB_HOST" "$db_host"
  set_env_value "$tenant_file" "DB_PORT" "$db_port"
  set_env_value "$tenant_file" "DB_NAME" "$db_name"
  set_env_value "$tenant_file" "DB_USER" "$db_user"
  set_env_value "$tenant_file" "DB_PASSWORD" "$db_password"
  set_env_value "$tenant_file" "DB_SCHEMA" "$db_schema"
  set_env_value "$tenant_file" "KEYCLOAK_ENABLED" "$keycloak_enabled"
  set_env_value "$tenant_file" "KEYCLOAK_URL" "$keycloak_url"
  set_env_value "$tenant_file" "KEYCLOAK_REALM" "$keycloak_realm"
  set_env_value "$tenant_file" "KEYCLOAK_CLIENT_ID" "$keycloak_client_id"
  set_env_value "$tenant_file" "KEYCLOAK_CLIENT_SECRET" "$keycloak_client_secret"
  set_env_value "$tenant_file" "KEYCLOAK_CALLBACK_URI" "$keycloak_callback"

  fix_permissions "$INSTALL_DIR"

  if [[ "$START_NOW" == "true" ]]; then
    info "Starting containers"
    if [[ -f "${INSTALL_DIR}/docker-compose.yml" ]]; then
      (cd "$INSTALL_DIR" && docker compose down 2>/dev/null || true)
    fi
    (cd "$INSTALL_DIR" && docker compose pull && docker compose up -d)
    info "Waiting for health check..."
    sleep 5
    if curl -fsS "http://127.0.0.1:8000${API_ROOT}/health" >/dev/null 2>&1; then
      info "Health check OK"
    else
      warn "Health check not ready yet — run: cd ${INSTALL_DIR} && docker compose logs -f app"
    fi
  fi

  echo
  info "Installation complete: ${INSTALL_DIR}"
  echo
  echo "  Tenant API:  ${public_url}${API_ROOT}/v1/"
  echo "  Admin API:   ${public_url}${API_ROOT}/admin/"
  echo "  Health:      ${public_url}${API_ROOT}/health"
  echo "  OpenAPI:     ${public_url}${API_ROOT}/v1/docs"
  echo
  echo "  Admin user:  admin"
  echo "  Admin pass:  ${admin_password}"
  echo
  echo "  Manage:"
  echo "    cd ${INSTALL_DIR}"
  echo "    docker compose ps"
  echo "    docker compose logs -f app"
  echo "    docker compose pull && docker compose up -d   # upgrade"
  echo
  echo "  Reverse proxy: see deploy/nginx.conf.example in the repo."
  echo "  Pin deploy templates: GISWATER_API_REF=v1.3.2 curl -fsSL .../deploy/install.sh | sudo bash"
  echo
}

main "$@"
