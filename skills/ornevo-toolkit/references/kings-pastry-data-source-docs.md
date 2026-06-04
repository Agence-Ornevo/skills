# Kings Pastry — Data Source Documentation Index

> **Last updated:** 2026-06-02 (v2 — archive tables added)

## Documentation Structure

Each dashboard has 3 doc types:
- **Synthesis** (`D0X_Data_Source_Synthesis.md`): KPIs, BC tables, blockers, build order
- **Per-KPI Detail** (`D0X_KPI[N]_[Name]_Data_Sources.md`): Formula, sources, joins, DAX, validation
- **Connection List** (`D0X_Data_Source_Connection_List.md`): BC OData endpoints + refresh status

D01 = merge dashboard (refs child dashboards). D08 = V2 deferred.

## File Inventory

| Dashboard | Synthesis | Per-KPI Docs | Connection List |
|-----------|-----------|-------------|----------------|
| D01 | ✅ | 4 files | ✅ |
| D02 | ✅ | 5 files | ✅ |
| D03 | ✅ | 8 files | ✅ |
| D04 | ✅ | 4 files | ✅ |
| D05 | ✅ | 4 files | ✅ |
| D06 | ✅ | 4 files | ✅ |
| D07 | ✅ | 5 files | ✅ (in D07 ref) |
| D08 | V2 | V2 | V2 |

**Total: 47 data source doc files across 8 dashboards.**

## ⚠️ CRITICAL: Archive Tables for Historical Order Data

Active order tables in BC only contain **open/active** records. Historical closed orders are in archive tables:

| Archive Table | Table # | Endpoint (TBC) | Dashboards Affected |
|---------------|---------|---------------|---------------------|
| SalesHeaderArchive | 5107 | `SalesHeaderArchive` | D02, D03, D05 |
| SalesLineArchive | 5108 | `SalesLineArchive` | D02, D03, D05 |
| PurchaseHeaderArchive | TBD | TBD | D05 (PO Adherence, Lead Time) |
| PurchaseLineArchive | TBD | TBD | D05 |
| ProdOrderArchive | TBD | TBD | D04 (Throughput, Schedule) |

**Without archive tables, all historical KPIs only see active orders.** Shine to confirm availability + endpoint names.

## BC Export Issues Found (Jun 2)

- `GLAccount-15` — **Never run** — needed for D06 SC Cost %
- `Finished_Production_Order_Excel` — not in export list — D04
- `PostedPurchaseInvoicesLine139` — not in export list — D05 PPV
- `Purchase_Order_ExcelPurchLines` — only 3 fields — needs more
- `PostedPurchaseReceiptsLine137` — only 2 fields — needs Item_Category_Code, UOM
- `Bin-7354` — only 2 fields — needs Zone_Code, capacity

**Action:** Shine to configure missing exports + add fields to under-configured ones.

## Per-KPI Doc Template

1. Definition (formula, target, unit, grain)
2. Data Sources table
3. Calculation Logic (DAX stub)
4. Filters/Slicers
5. Join Logic (text diagram)
6. Notes (blockers, build order)
7. Validation (expected values)

## Shared Reference

For stakeholders, schedule, GL accounts, ENT-T07, thresholds → `kings-pastry.md` in this directory.
