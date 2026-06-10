# TMDL Format & Indentation Guide

## Indentation Rules (TE3 TMDL View)

**CRITICAL: `displayFolder` must be at exactly 3 tabs.** This is the only indentation level TE3 recognizes. Wrong indentation = measure created but display folder NOT applied.

### Working Pattern (Confirmed from OTIF)

```
createOrReplace
\tref table _Measures
\t\tmeasure '_Name' =
\t\t\t\tVAR _x = 1
\t\t\t\tRETURN _x
\t\t\tdisplayFolder: D02\_Folder

\t\tmeasure '_Name2' = [_Name]
\t\t\tdisplayFolder: D02\_Folder
```

Tab levels:
| Element | Tabs |
|---------|------|
| `createOrReplace` | 0 |
| `ref table _Measures` | 1 |
| `measure '...' =` | 2 |
| Multi-line DAX body | 4 |
| Single-line DAX | 3 |
| `displayFolder:` | **3** (CRITICAL) |

### Verification Command

```bash
head -8 file.tmdl | cat -et
# displayFolder lines should show: ^I^I^IdisplayFolder
```

## Table Name Escaping

Table/view names must **never** contain backslashes. Only displayFolder uses backslashes.

**WRONG:** `v_D02\_FillRate_Daily` (backslash in table name)
**RIGHT:** `v_D02_FillRate_Daily` (underscore), `D02\_FillRate` (display folder)

**Fix pattern:**
```python
import re
content = re.sub(r'v_D02\\_([A-Za-z0-9]+_Daily)', r'v_D02_\1', content)
```

## pyodbc CREATE VIEW Pattern

pyodbc `execute()` allows only one statement. Two-step process required:

```python
import re
cursor.execute("DROP VIEW IF EXISTS pbi.v_X")
conn.commit()
sql = re.sub(r"CREATE\s+OR\s+ALTER\s+VIEW", "CREATE VIEW", sql, flags=re.IGNORECASE)
cursor.execute(sql)
conn.commit()
cursor.execute("SELECT COUNT(*) FROM pbi.v_X")  # verify
```

**Important:** `CREATE OR ALTER VIEW` silently fails if the view doesn't already exist. Always use `DROP VIEW IF EXISTS` + `CREATE VIEW` for first-time creation.

**Important:** Bracket reserved words in pyodbc SQL strings: `[LineNo]` not `LineNo`.

## Pre-Execution Audit

```python
import re, os

def audit_tmdl(filepath):
    with open(filepath) as f:
        content = f.read()
    issues = []
    
    # Bad table name escapes (backslash in table name, not displayFolder)
    bad = re.findall(r'v_D02\\[^\[]+', content)
    if bad:
        issues.append(f"Bad table refs: {set(bad)}")
    
    # displayFolder not at 3 tabs
    for i, line in enumerate(content.split('\n')):
        if 'displayFolder:' in line:
            tabs = len(line) - len(line.lstrip('\t'))
            if tabs != 3:
                issues.append(f"Line {i+1}: displayFolder at {tabs} tabs (should be 3)")
    
    # Mixed tabs/spaces in DAX
    for i, line in enumerate(content.split('\n')):
        if any(line.strip().startswith(kw) for kw in ['VAR ', 'RETURN ', 'CALCULATE']):
            if '\t' in line and '    ' in line.replace('\t', ''):
                issues.append(f"Line {i+1}: mixed tabs/spaces")
    
    # Stockout Ing inverted logic check
    if 'StockoutIng' in os.path.basename(filepath):
        if '_up = _d >= 0' in content:
            issues.append("StockoutIng _up should be _d <= 0 (lower is better)")
    
    return issues
```

## M Import Script Column Verification

Always verify M script column names match actual view output:

```sql
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA='pbi' AND TABLE_NAME='<view>'
ORDER BY ORDINAL_POSITION
```

**Common mismatches this session:**
- ReqPromAdh view outputs `DocumentNo` (not `No`)
- ReqPromAdh view has `PostingDate` (not `ShipmentDate`)
- Stockout view has `SnapshotDate` (not `ShipmentDate`)

## KPI Date Column Reference Table

| KPI | View | Date Column |
|-----|------|-------------|
| OTIF | v_D02_OTIF_Daily | ShipmentDate |
| On-Time | v_D02_OnTime_Daily | ShipmentDate |
| Fill Rate | v_D02_FillRate_Daily | ShipmentDate |
| Req/Prom Adh | v_D02_ReqPromAdh_Daily | **PostingDate** |
| Stockout FG | v_D02_Stockout_Daily | **SnapshotDate** |
| Stockout Ing | v_D02_Stockout_Daily | **SnapshotDate** |

Every `_Period`, `_Period Prior`, and `_Line` measure must reference the correct date column.
