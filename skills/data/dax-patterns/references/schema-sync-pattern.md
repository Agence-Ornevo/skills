# Schema Sync Script Patterns — Kings Pastry

## Daily Schema Synchronization Workflow

### Purpose
Keep Kings Pastry DataBase documentation in sync with the live Azure SQL schema. Run daily via cron during active development (D02-D08 dashboard builds).

### Files Involved
- `extract_schema.py` — Fresh schema extraction (columns, PKs, FKs, indexes)
- `compare_schema.py` — Diff against previous extraction and .md docs
- `current_schemas.json` — Latest extraction (replaces previous)
- `current_schemas_previous.json` — Backup of previous extraction
- `schema_comparison.json` — Detailed diff output
- `Schemas/*.md` — Per-table documentation files
- `Relationships/D02_Relationships.md` — ER diagram and relationship matrix
- `Validation/D02_Validation_Queries.md` — Pre/post build validation queries
- `README.md` — Master index with sync timestamp

### Key Findings (2026-06-09)

1. **`az` CLI not on PATH in cron** — Use `/opt/homebrew/bin/az` explicitly
2. **`execute_code` blocked in cron mode** — Use `write_file` + `terminal` for Python scripts
3. **`pyodbc` may need install** — `pip3 install pyodbc` (one-time)
4. **`patch` tool modes** — Only `mode='replace'` and `mode='patch'` exist, NOT `mode='new_string'`
5. **f-strings with `%` in write_file** — Python `%` format specifiers in content strings can get mangled; use `.format()` or explicit `%` escaping

### extract_schema.py Pattern

```python
#!/usr/bin/env python3
"""Extract full schema for all Kings Pastry tables."""
import subprocess, json, struct, pyodbc

def get_token():
    result = subprocess.run(
        ["/opt/homebrew/bin/az", "account", "get-access-token",
         "--resource", "https://database.windows.net/",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip()

def get_conn(token):
    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack("<I", len(token_bytes)) + token_bytes
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=kingsbi-sqlsrv-prod.database.windows.net;"
        "DATABASE=DataWarehousePBI;"
        "Encrypt=yes;TrustServerCertificate=no;"
    )
    return pyodbc.connect(conn_str, attrs_before={1256: token_struct}, timeout=30)
```

### compare_schema.py Pattern

Compares fresh extraction against:
1. Previous `current_schemas.json` (new/dropped/type-changed columns)
2. Existing `.md` files (column count discrepancies)

Outputs `schema_comparison.json` with per-table change details.

### Alert Conditions

Alert Hernan when:
- Connection fails (AAD token expired, network down)
- Schema drift detected (new/dropped/type-changed columns)
- New tables found in schema
- Row count anomalies (>10% change)

### No-Drift Report Format

When no changes detected, still update:
- All .md header timestamps
- README.md sync timestamp and drift status
- current_schemas.json (replace with fresh)
- Row count / date range data in .md files
