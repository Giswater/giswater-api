#!/usr/bin/env bash
# Post-deploy smoke: run against a live instance (default http://127.0.0.1:8000).
# Usage: BASE_URL=... TENANT_HOST=... APEX_HOST=... ./scripts/smoke_test.sh
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
TENANT_HOST="${TENANT_HOST:-test.bgeo360.com}"
APEX_HOST="${APEX_HOST:-bgeo360.com}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-}"

if [[ -z "${ADMIN_PASS}" ]]; then
  echo "ERROR: ADMIN_PASS is required (do not rely on default credentials)." >&2
  exit 1
fi

echo "==> GET ${BASE_URL}/health"
curl -sS -f "${BASE_URL}/health" | (command -v jq >/dev/null && jq . || cat)
echo

echo "==> GET ${BASE_URL}/gw-api/v1/ready  Host: ${TENANT_HOST}"
curl -sS -f -H "Host: ${TENANT_HOST}" "${BASE_URL}/gw-api/v1/ready" | (command -v jq >/dev/null && jq . || cat)
echo

echo "==> GET ${BASE_URL}/admin/tenants  Host: ${APEX_HOST}  (HTTP Basic)"
curl -sS -f -u "${ADMIN_USER}:${ADMIN_PASS}" -H "Host: ${APEX_HOST}" "${BASE_URL}/admin/tenants" | (command -v jq >/dev/null && jq . || cat)
echo

echo "==> OK"
