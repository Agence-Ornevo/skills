#!/usr/bin/env bash
# verify-credentials.sh — Checks all API keys respond 200
# Usage: ./verify-credentials.sh

set -euo pipefail

echo "🔍 Ornevo Agency — Credential Verification"
echo "=========================================="

# Load environment (expects keys in env or .env)
if [[ -f .env ]]; then
    source .env
fi

check_endpoint() {
    local name="$1"
    local url="$2"
    local header="$3"
    local expected="${4:-200}"

    echo -n "  $name... "
    code=$(curl -s -o /dev/null -w "%{http_code}" -H "$header" "$url" || echo "000")
    if [[ "$code" == "$expected" ]]; then
        echo "✅ $code"
    else
        echo "❌ $code (expected $expected)"
        return 1
    fi
}

# n8n
if [[ -n "${N8N_API_KEY:-}" ]]; then
    check_endpoint "n8n (workflows)" "https://n8n.ornevo.pro/api/v1/workflows?active=true&limit=1" "X-N8N-API-KEY: $N8N_API_KEY"
else
    echo "  n8n... ⚠️ N8N_API_KEY not set"
fi

# Bitrix24
if [[ -n "${BITRIX24_WEBHOOK_URL:-}" ]]; then
    check_endpoint "Bitrix24 (deals)" "$BITRIX24_WEBHOOK_URL/crm.deal.list?limit=1" ""
else
    echo "  Bitrix24... ⚠️ BITRIX24_WEBHOOK_URL not set"
fi

# Brevo
if [[ -n "${BREVO_API_KEY:-}" ]]; then
    check_endpoint "Brevo (account)" "https://api.brevo.com/v3/account" "api-key: $BREVO_API_KEY"
else
    echo "  Brevo... ⚠️ BREVO_API_KEY not set"
fi

# Linear
if [[ -n "${LINEAR_API_KEY:-}" ]]; then
    check_endpoint "Linear (viewer)" "https://api.linear.app/graphql" "Authorization: Bearer $LINEAR_API_KEY" "200"
else
    echo "  Linear... ⚠️ LINEAR_API_KEY not set"
fi

# Notion
if [[ -n "${NOTION_API_KEY:-}" ]]; then
    check_endpoint "Notion (self)" "https://api.notion.com/v1/users/me" "Authorization: Bearer $NOTION_API_KEY" "200"
else
    echo "  Notion... ⚠️ NOTION_API_KEY not set"
fi

# Plane
if [[ -n "${PLANE_API_KEY:-}" ]]; then
    check_endpoint "Plane (projects)" "https://pm.ornevo.pro/api/v1/projects/" "Authorization: Bearer $PLANE_API_KEY"
else
    echo "  Plane... ⚠️ PLANE_API_KEY not set"
fi

echo ""
echo "✅ Verification complete"