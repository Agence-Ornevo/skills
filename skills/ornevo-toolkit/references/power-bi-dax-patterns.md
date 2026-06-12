# Power BI DAX Build Patterns — Kings Pastry D02-D08

> Reference for building DAX measures in Power BI Desktop for Kings Pastry dashboards.
> Updated: 2026-06-04

## Measure Naming Convention (D07-style)

One measure per element. NO shared SWITCH dispatcher.

```
_KPI_Total       — denominator (all eligible records)
_KPI_Var         — "bad" records (failures/errors)
_KPI_Base        — DIVIDE(Total - Var, Total)
_KPI_Value       — wrapper: [_KPI_Base]
_KPI_Target      — from KPIConfig lookup
_KPI_Period      — responds to YTD/MTD/MTO slicer
_KPI_Period_Prior — same period, 1 year back
_KPI_Delta       — Period vs Period Prior
_KPI_Delta_Label — "▲ 1.2%"
_KPI_Chip_Color  — green/red text
_KPI_Chip_BG_Color — green/red background
```

## Build Order

1. `_KPI_Total` → validate returns > 0
2. `_KPI_Var` → validate returns ≥ 0 and < Total
3. `_KPI_Base` → validate returns 0-1 range
4. `_KPI_Value` → same as Base
5. `_KPI_Target` → from KPIConfig
6. `_KPI_Period` → validate changes with slicer
7. `_KPI_Period_Prior` → validate returns value for prior year
8. `_KPI_Delta` → Period - Prior
9. `_KPI_Delta_Label` → formatted text
10-11. Chip Colors → green/red based on goal direction

## Critical DAX Pitfalls

| Wrong | Correct | Why |
|-------|---------|-----|
| `NOT BLANK(x)` | `NOT ISBLANK(x)` | `BLANK()` takes 0 args |
| `SELECTEDVALUE` on composite keys | `MAX()` | Composite key error |
| `FILTER(ALL('Date'), ...)` | `DATESBETWEEN` | Overrides active relationship |
| `bc.SalesLine` | `SalesLine` | PBI strips schema prefix |

## Data Source Gotchas

- `bc.SalesLine` ShipmentDate/PromisedDeliveryDate mostly BLANK → use `SalesLineArchive`
- `pbi.DailyInventorySnapshot` has all dates → use for Stockout KPIs
- `KPIConfig`: KPIName, TargetMonth, Goal (higher/lower) — disconnected table
- `Axis Period`: composite key → `MAX('Axis Period'[Axis Period])`
- Only ONE active date relationship per table