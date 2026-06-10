# n8n API Key Configuration Fix

## Problem Discovered (2026-06-07)

The n8n MCP server (`mcp_n8n_*`) returns 401 Unauthorized because it's configured with the wrong API key.

### Current (Broken) Key
- **Label**: "MCP Server API Key"
- **Audience**: `mcp-server-api`
- **Scopes**: `[]` (empty — no permissions)
- **User**: `projet@ornevo.fr` (Hernán)

### Correct Key
- **Label**: "hermes-agent"
- **Audience**: `public-api`
- **Scopes**: Full (workflow:read, workflow:list, execution:read, execution:list, workflow:activate, workflow:deactivate, etc.)
- **User**: `projet@ornevo.fr` (Hernán)
- **Format**: JWT (267 chars, starts with `eyJhbG...`)

## Root Cause
When the MCP server was configured, it used the "MCP Server API Key" which is scoped for `mcp-server-api` audience only — this audience has no permissions granted in n8n's RBAC. The "hermes-agent" key was created for external API access with `public-api` audience and full scopes.

## Fix Required
Update the n8n MCP server configuration (in Hermes config or n8n MCP server env) to use the "hermes-agent" JWT key instead of "MCP Server API Key".

### API Header Format
```bash
# WRONG (current MCP behavior)
Authorization: Bearer <MCP_SERVER_API_KEY>

# CORRECT (n8n REST API expectation)
X-N8N-API-KEY: <HERMES_AGENT_JWT>
```

The n8n REST API expects `X-N8N-API-KEY` header, not `Authorization: Bearer`.

## Extraction Method (Verified Working)

```bash
# On production server (91.134.67.56)
ssh ubuntu@91.134.67.56 "docker exec n8n-db psql -U n8n -d n8n -c \"COPY (SELECT \\\"apiKey\\\" FROM user_api_keys WHERE label='hermes-agent') TO '/tmp/hermes_key.txt';\" && cat /tmp/hermes_key.txt"
```

Returns full JWT (267 chars). Save to Hermes config for n8n MCP server.

## Verification
```bash
# Test with correct key
curl -H "X-N8N-API-KEY: <JWT>" https://n8n.ornevo.pro/api/v1/workflows?active=true
# Should return 200 with workflow list
```

## Related Files
- `scripts/extract-n8n-jwt.py` — automated extraction script
- Hermes config: `~/.hermes/profiles/ornevo-agency/config.yaml` (mcpServers.n8n)