# D02 — Service & Fulfillment: Build Guide

> **Last updated:** 2026-06-04
> **Status:** Build plan complete, awaiting template analysis + column verification
> **Folder:** `D02_Service_Fulfillment/` (in Kings-pastry repo)

## Folder Structure

```
D02_Service_Fulfillment/
  Build/
    D02_Build_Plan.md              ← Master build plan (OTIF-first)
    D02_Template_Analysis.md       ← Phase 0 output (fill from D07 V2)
  Data_Sources/
    D02_Data_Source_Map.md         ← BC tables, pbi views, relationships
    D02_SQL_Queries.md             ← Validation queries
  DAX/
    D02_DAX_Measures.md            ← All 6 KPI measures + date table + calc group
    D02_Date_Table_DAX.md          ← Date table + calculation group
  Documentation/
    D02_KPI_Definitions.md         ← KPI specs from wireframe V9 + spec V6
    D02_Slicer_Rules.md            ← Slicer applicability
    D02_L2_L3_Grain.md             ← Detail table grain
  Validation/
    D02_Validation_Checklist.md    ← SQL queries + DAX cross-checks
    D02_Data_Quality_Notes.md
```

## Build Strategy: OTIF First

OTIF is the anchor KPI — most complex, most shared across dashboards. Building it first validates the entire data model (SalesLine ↔ SalesShipmentLine ↔ SalesShipmentHeader join).

### Build Order

| Phase | KPI | Complexity | Depends On |
|-------|-----|-----------|------------|
| 1 | KPI-1 OTIF | High | bc.SalesLine + bc.SalesShipmentLine + bc.SalesShipmentHeader |
| 2 | KPI-2 On-Time Shipment | Low | Same tables as OTIF |
| 3 | KPI-3 Fill Rate | Low | Same tables + Document_Date relationship |
| 4 | KPI-6 Req vs Promised | Low | bc.SalesHeader only |
| 5 | KPI-4 Stockout FG | Medium | pbi.DailyInventorySnapshot + FG code |
| 6 | KPI-5 Stockout Ingredients | Medium | pbi.DailyInventorySnapshot + RAW code |

### Prerequisites (Phase 0)

Before building any DAX:
1. Open D07 V2 PBIX → extract date table, calc group, PeriodSelection structure
2. Run SQL validation queries (especially pbi.DailyInventorySnapshot columns + FG/RAW codes)
3. Copy D07 V2 as D02.pbix working file

### Key Data Sources

**bc schema:** SalesHeader, SalesLine, SalesShipmentHeader, SalesShipmentLine, Item, ItemCategory, ItemLedgerEntry, Customer

**pbi schema:** DailyInventorySnapshot (pre-built daily stock snapshot — eliminates running balance calculations)

### Critical Open Blockers

| # | Item | Blocks | Resolution |
|---|------|--------|------------|
| 1 | FG posting group code | KPI-4 | `SELECT DISTINCT Inventory_Posting_Group FROM bc.Item` |
| 2 | RAW posting group code | KPI-5 | Same query |
| 3 | pbi.DailyInventorySnapshot columns | KPI-4, KPI-5 | `SELECT TOP 5 * FROM pbi.DailyInventorySnapshot` |
| 4 | ENT-217 Channel column name | Channel slicer | Ask Shine |
| 5 | On-time tolerance window | KPI-1, KPI-2 | Default 0d, flag for client |

### Period × Granularity Defaults

| Period | Granularity | X-axis Field |
|--------|------------|-------------|
| YTD | Weekly | Date[Week Label] |
| MTD | Daily | Date[Date] |
| MTO | Monthly | Date[Month Label] |

### Calculation Group "TI" (reuse D07 pattern)

- **Current** — responds to PeriodSelection slicer
- **Latest Month** — always current month
- **Prior Year** — same period PY
- **Sparkline** — no date filter

### Date Table Relationships

| KPI | Date Field | Relationship |
|-----|-----------|-------------|
| OTIF, OnTime | bc.SalesShipmentHeader.Posting_Date | Active |
| FillRate, ReqPromAdh | bc.SalesHeader.Document_Date | Inactive (USERELATIONSHIP) |
| StockoutFG, StockoutIng | pbi.DailyInventorySnapshot.Snapshot_Date | Inactive (USERELATIONSHIP) |

### Slicer Applicability

| Slicer | Applicable | Join Path |
|--------|-----------|-----------|
| Period View | Yes | Date field on all fact tables |
| Channel Mix | Partial | ENT-217 file (SharePoint) — column name TBD |
| Country | Yes | bc.Customer[Country_Region_Code] |
| Region | Partial | Indirect via Customer → Ship-to Address |
| Product Category | Yes | bc.ItemCategory[Parent_Category] |

### KPI Targets

| KPI | Target | Unit | Goal |
|-----|--------|------|------|
| OTIF | 95 | % | Higher |
| On-Time Shipment | 95 | % | Higher |
| Fill Rate | 98 | % | Higher |
| Stockout Rate FG | 5 | % | Lower |
| Stockout Rate Ingredients | 5 | % | Lower |
| Req vs Promised Adherence | 95 | % | Higher |

### Removed KPIs

- Delivery Delay Rate — removed from scope
- Order Cycle Time — removed from scope

### Wireframe Reference

- Source of truth: ControlTowerV9.html (D02 tab)
- KPI spec: KPI_Data_Spec_Template_V6.xlsx (D02_Service sheet)
- Documentation: Phase 1 - Visibility/Deliverables/1. Wireframes/Documentation/D02 - Service & Fulfillment - Documentation.md
