# Plane API Reference

## Overview
Plane (https://pm.ornevo.pro) is Ornevo's self-hosted project management tool (open-source Linear alternative). Used for issue tracking, sprint planning, and client approval workflows.

## Base URL
`https://pm.ornevo.pro/api/v1/`

## Authentication
Personal API token via `Authorization: Bearer <token>` header.
Get token: Plane → Settings → API → Generate Personal Token

## Key Endpoints

### Projects
- `GET /projects/` — List all projects
- `GET /projects/{project_id}/` — Get project details
- `GET /projects/{project_id}/issues/` — List issues in project

### Issues (Work Items)
- `GET /issues/` — List issues with filters
- `GET /issues/{issue_id}/` — Get issue details
- `PATCH /issues/{issue_id}/` — Update issue (state, assignee, etc.)

### Issue Filters (Query Params)
| Param | Example | Description |
|-------|---------|-------------|
| `project` | `project_id` | Filter by project |
| `state` | `state_id` | Filter by state (backlog, todo, in_progress, in_review, done) |
| `assignee` | `user_id` | Filter by assignee |
| `label` | `label_id` | Filter by label |

## Approval Workflow Mapping
Plane states used for client approvals:
- `in_review` — "Waiting for Client Approval"
- `approved` — "Client Approved"
- `changes_requested` — "Client Requested Changes"

## Example: Find Pending Approvals >2 Days
```bash
# Get state IDs first
curl -H "Authorization: Bearer $PLANE_API_KEY" \
  https://pm.ornevo.pro/api/v1/projects/{project_id}/issue-states/

# Query issues in "in_review" state updated >2 days ago
curl -H "Authorization: Bearer $PLANE_API_KEY" \
  "https://pm.ornevo.pro/api/v1/issues/?project={project_id}&state={in_review_state_id}&updated_at__lt=2026-06-06"
```

## Rate Limits
- 1000 requests/hour per token
- Standard REST pagination (`page`, `page_size`)

## Webhook Support
Plane supports webhooks for real-time updates:
- Configure: Project → Settings → Webhooks
- Events: `issue.created`, `issue.updated`, `issue.state_changed`
- Payload includes issue data and changed fields

## Integration Notes
- Plane API is REST (not GraphQL like Linear)
- Uses numeric IDs (not UUIDs like Linear)
- State machines are per-project (not global)
- Labels are project-scoped