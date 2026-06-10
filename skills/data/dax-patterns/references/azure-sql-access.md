# Azure SQL Access Patterns — Kings Pastry

## Connection Details

| Parameter | Value |
|-----------|-------|
| Server | `kingsbi-sqlsrv-prod.database.windows.net` |
| Database | `DataWarehousePBI` |
| Auth Type | Azure AD (no SQL auth) |
| AAD Admin | `SCM Analytics` group |
| Azure CLI User | `scm_analytics1@kingspastry.com` |
| Subscription | King's Pastry Azure Subscription |
| Resource Group | `kp-rg-dataplatform` |

## pyodbc + AAD Token (Recommended for scripting)

**Prerequisites (one-time):**
```bash
brew tap microsoft/mssql-release https://github.com/microsoft/homebrew-mssql-release
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18
pip3 install pyodbc
```

**IMPORTANT -- PATH in cron/scheduled contexts:**
The `az` CLI is NOT on PATH in cron jobs. Always use full path:
```python
import subprocess, struct, pyodbc

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

## Schema Inspection Queries

```sql
-- Full schema extraction
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH,
       NUMERIC_PRECISION, NUMERIC_SCALE, COLUMN_DEFAULT, ORDINAL_POSITION
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA='?' AND TABLE_NAME='?'
ORDER BY ORDINAL_POSITION;

-- Actual PK constraints (NOT business keys)
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA='?' AND TABLE_NAME='?'
AND CONSTRAINT_NAME LIKE 'PK%';

-- Foreign keys
SELECT fk.COLUMN_NAME,
       pk.TABLE_SCHEMA + '.' + pk.TABLE_NAME,
       pk.COLUMN_NAME
FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
WHERE fk.TABLE_SCHEMA='?' AND fk.TABLE_NAME='?';
```

## Kings Pastry Schema Facts (verified 2026-06-09)

### PK Pattern: BC tables use SystemId, NOT business keys

All BC tables in the DWH use `SystemId` (uniqueidentifier, NOT NULL) as the actual PK constraint. Business keys (No, DocumentNo+LineNo, Code) are NOT enforced as PKs. This is expected -- the DWH is an ADF-replicated copy.

Table | Business Key | Actual PK
----- | ------------ | --------
bc.SalesHeader | No | SystemId
bc.SalesLine | DocumentNo + LineNo | SystemId
bc.SalesHeaderArchive | No | SystemId
bc.SalesLineArchive | DocumentNo + LineNo | SystemId
bc.Item | No | SystemId
bc.ItemCategory | Code | SystemId
bc.Customer | No | SystemId

### pbi tables have meaningful PKs

pbi.DailyInventorySnapshot: PK = SnapshotDate + LocationCode + ItemNo
pbi.KPIConfig: PK = KPIName + Dashboard

### Column Counts (2026-06-09)

Table | Columns | Rows | Date Range
----- | ------- | ---- | ----------
bc.SalesHeader | 205 | 315 | 2022-05-24 to 2026-08-03
bc.SalesLine | 209 | 2,761 | --
bc.SalesHeaderArchive | 170 | 59,873 | 2020-07-03 to 2026-06-05
bc.SalesLineArchive | 181 | 388,267 | 2020-07 to 2026-06
bc.Item | 179 | 3,083 | --
bc.ItemCategory | 15 | 77 | --
bc.Customer | 122 | 1,716 | --
pbi.DailyInventorySnapshot | 10 | 97,525 | 2025-01-02 to 2026-06-06
pbi.KPIConfig | 11 | 0 | EMPTY -- needs population
