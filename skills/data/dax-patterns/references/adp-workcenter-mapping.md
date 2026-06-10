# ADP ↔ BC Work Center Mapping Investigation — Kings Pastry D04/D07

## Executive Summary (2026-06-07)

Investigation of how to relate SharePoint ADP work hours reports to BC work centers and production orders. **Critical blockers found** for D04/D07 Labour KPIs.

---

## Key Tables

| Table | Rows | Purpose |
|-------|------|---------|
| `scm.ADPBCWorkCenterMapping` | 60 | Maps ADP Dept Codes → BC Work Centre Names (NOT BC WorkCenter.No codes) |
| `bc.WorkCenter` | 31 | Master work centers — PK = `No` (e.g., `CAKE`, `F_MIX`, `H_BACK_MIX`) |
| `bc.ProductionOrder` | ~20+ | Production orders — has `RoutingNo` (e.g., `RT00284`), NO `WorkCenterCode` |

---

## Mapping Mismatch: 22 Mapped vs 31 Actual Work Centers

| ADP Dept | Mapping `BCWorkCentreNo` | Actual `bc.WorkCenter.No` | Match? |
|----------|--------------------------|---------------------------|--------|
| BMIX00 | BATTER MIX_HOBART | H_BACK_MIX / D_BACK_MIX | ❌ Name mismatch |
| BMIX00 | BTTER MIX_ITALY | I_BACK_MIX | ❌ Name mismatch |
| CKL-00 | CAKE LINE | CAKE | ❌ Name mismatch |
| CKL-00 | CREAM KETTLE | B_KETTLE / F_STEAM | ❌ Name mismatch |
| FMIX00 | CREAM MIX_HOBART | H_BACK_MIX / F_MIX | ❌ Name mismatch |
| FMIX00 | CREAM MIX_ITALY_MIXER | I_BACK_MIX / F_MIX | ❌ Name mismatch |
| **GBL-00** | **GB_JELLO_BIG** | **GB_JELLO_BIG** | ✅ **EXACT** |
| **GBL-00** | **GB_JELLO_SM** | **GB_JELLO_SM** | ✅ **EXACT** |
| GBL-00 | GB_PWDR | GB_PWDR_PKG | ❌ Close |
| JRL-00 | JELLY ROLL LINE | JELLY | ❌ Name mismatch |
| PFL-00 | FRONT MIX | F_MIX | ❌ Name mismatch |
| PFL-00 | PASTRY DOUGH MIX | D_BACK_MIX / PREMIX | ❌ |
| PFL-00 | PASTRY LAMINATION | — | ❌ No match |
| **PFL-00** | **PUFF** | **PUFF** | ✅ **EXACT** |
| **PFL-00** | **SUPPORT** | **SUPPORT** | ✅ **EXACT** |
| **TSL-00** | **T DOUGH C** | **T DOUGH C** | ✅ **EXACT** |
| TSL-00 | TART CUTTER/SHEETER/FORMER | TART | ❌ Name mismatch |

**Only 5 of 22 mapped work centers match exactly** (GB_JELLO_BIG, GB_JELLO_SM, PUFF, SUPPORT, T DOUGH C).

---

## Production Order → Work Center Link: BROKEN

**`bc.ProductionOrder` has NO `WorkCenterCode` column.** It has:
- `RoutingNo` (e.g., `RT00284`, `RT00282`, `RT00168`)
- `LocationCode` (always `PLANT`)

**No routing tables exist** in the database:
- `bc.Routing` — NOT FOUND
- `bc.RoutingLine` — NOT FOUND
- `bc.ProdOrderRoutingLine` — NOT FOUND

---

## Impact on D04/D07 Labour KPIs

| KPI | Requirement | Current Block |
|-----|-------------|---------------|
| D04 Labour (72 cs/lh) | ADP hours → BC work center → Production Order | Mapping uses friendly names, not BC codes; no routing tables |
| D07 Labour (22 cs/lh) | Same chain | Cannot compute without routing → work center → ADP hours |

---

## Required Client Actions

1. **Fix `scm.ADPBCWorkCenterMapping.BCWorkCentreNo`** — Update to use actual `bc.WorkCenter.No` codes:
   ```
   CAKE LINE → CAKE
   BATTER MIX_HOBART → H_BACK_MIX (or D_BACK_MIX)
   CREAM MIX_HOBART → F_MIX (or H_BACK_MIX)
   JELLY ROLL LINE → JELLY
   FRONT MIX → F_MIX
   PASTRY DOUGH MIX → D_BACK_MIX
   ```

2. **Provide routing tables** — Need `bc.Routing` and `bc.RoutingLine` (WorkCenterCode per operation) from BC export or SQL DWH to link ProductionOrder → WorkCenter

3. **Define ADP "Production-*" rows** (rows 27-44) — Currently all `BCWorkCentreNo = NULL`; group-level mappings needing allocation logic

4. **Clarify exclusions** — Rows 23, 25, 26, 39, 46-60 marked "Not defined yet" or office/warehouse — exclude from production labour KPIs?

---

## Verification Queries Used

```sql
-- Work center master
SELECT No, Name, WorkCenterGroupCode FROM bc.WorkCenter ORDER BY No;

-- Mapping table
SELECT ADPDeptCode, ADPDescription, BCWorkCentreNo, Notes FROM scm.ADPBCWorkCenterMapping;

-- Join test
SELECT m.ADPDeptCode, m.BCWorkCentreNo, wc.No as WC_No, wc.Name as WC_Name, wc.WorkCenterGroupCode
FROM scm.ADPBCWorkCenterMapping m
LEFT JOIN bc.WorkCenter wc ON m.BCWorkCentreNo = wc.No
WHERE m.BCWorkCentreNo IS NOT NULL AND m.BCWorkCentreNo <> 'Not defined yet';

-- Production order sample
SELECT No, Status, RoutingNo, LocationCode FROM bc.ProductionOrder;

-- Check for routing tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA='bc' AND (TABLE_NAME LIKE '%Routing%' OR TABLE_NAME LIKE '%Rout%');
```

---

## Next Steps for Dashboard Build

1. **Share mismatch table with client** — Show 5 exact matches vs 17 mismatches
2. **Request routing tables** — `bc.Routing` + `bc.RoutingLine` from BC export
3. **Update mapping table** — Fix `BCWorkCentreNo` to match `bc.WorkCenter.No` codes
4. **Build join logic** once routing exists:
   ```
   ProductionOrder.RoutingNo → RoutingLine.WorkCenterCode → WorkCenter.No 
   ← ADPMapping.BCWorkCentreNo → ADP hours
   ```