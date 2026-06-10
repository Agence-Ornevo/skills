# KPIConfig Table — Kings Pastry (Authoritative Dump)

**Server:** `kingsbi-sqlsrv-prod.database.windows.net` / `DataWarehousePBI`
**Schema:** `pbi.KPIConfig`
**Verified:** 2026-06-09

## Complete Table Data

| KPIName | Dashboard | KPIID | Goal | TargetDay | TargetWeek | TargetMonth | Unit | WarnMin | WarnMax |
|---------|-----------|-------|------|-----------|------------|-------------|------|---------|---------|
| Capacity Utilization % | D07 | KPI-CAPUTIL | range | 0.85 | 0.85 | 0.85 | % | 0.80 | 0.95 |
| Days On Hand FG | D | KPI-DOH-FG | lower | 14 | 14 | 14 | days | 0 | 0 |
| Days On Hand Ingredients | D | KPI-DOH-ING | lower | 10 | 10 | 10 | days | 0 | 0 |
| Days On Hand Packaging | D | KPI-DOH-PKG | lower | 10 | 10 | 10 | days | 0 | 0 |
| Fill Rate % | D | KPI-FILLRATE | higher | 0.95 | 0.95 | 0.95 | % | 0 | 0 |
| Inbound PO Adherence % | D05 | KPI-INBOUND-PO | higher | 0.90 | 0.90 | 0.90 | % | 0 | 0 |
| Inventory Accuracy % | D07 | KPI-INVACC | higher | 0.99 | 0.99 | 0.99 | % | 0 | 0 |
| Lead-Time Adherence % | D05 | KPI-LEADTIME | higher | 0.85 | 0.85 | 0.85 | % | 0 | 0 |
| On-Time Shipment % | D | KPI-ONTIMESHIP | higher | 0.90 | 0.90 | 0.90 | % | 0 | 0 |
| OTIF % | D | KPI-OTIF | higher | 0.95 | 0.95 | 0.95 | % | 0 | 0 |
| Outbound Freight Cost | D | KPI-OUTFREIGHT | lower | 2553.19 | 12765.96 | 50000 | $ | 0 | 0 |
| Outbound Target | D07 | KPI-LABOUR | higher | 10000 | 20000 | 20000 | cs | 0 | 0 |
| Picking Accuracy % | D07 | KPI-PICKACC | higher | 0.995 | 0.995 | 0.995 | % | 0 | 0 |
| Production Throughput | D | KPI-THROUGHPUT | higher | 0.90 | 0.90 | 0.90 | % | 0 | 0 |
| Purchase Price Variance | D05 | KPI-PPV | lower | 0 | 0 | 0 | % | 0 | 0 |
| SC Cost % of Revenue | D | KPI-SCCOST | lower | 0.12 | 0.12 | 0.12 | % | 0 | 0 |
| Schedule Adherence % | D | KPI-SCHEDADH | higher | 0.90 | 0.90 | 0.90 | % | 0 | 0 |
| Stockout Rate FG % | D | KPI-STOCKOUT-FG | lower | 0.02 | 0.02 | 0.02 | % | 0 | 0 |
| Stockout Rate Ingredients % | D02 | KPI-STOCKOUT-ING | lower | 0.02 | 0.02 | 0.02 | % | 0.00 | 0.05 |
| Storage Cost | D | KPI-STORAGE | lower | 4085.11 | 20425.53 | 80000 | $ | 0 | 0 |
| Supplier Spend Expouse | D05 | KPI-SSE | lower | 0.20 | 0.20 | 0.20 | % | 0 | 0 |

## Key Rules

1. **KPIID is canonical** — shared across dashboards. Never prefix with dashboard code.
2. **Dashboard column** is a dimension (D = Executive, D02 = Service, D05 = Procurement, D07 = Warehouse).
3. **Goal column** drives chip color logic: `higher` = `_d >= 0` is green, `lower`/`range` requires inversion.
4. **TargetDay/TargetWeek/TargetMonth** — use `TargetMonth` for DAX card measures.
5. **StockoutIng was INSERTED 2026-06-09** — is the only row with IsConfirmed=1 (all others = 0/false).

## D02 KPIID Lookup (Quick Reference)

| Measure | KPIID | TargetMonth |
|---------|-------|-------------|
| _OTIF Target | KPI-OTIF | 0.95 |
| _OnTime Target | KPI-ONTIMESHIP | 0.90 |
| _FillRate Target | KPI-FILLRATE | 0.95 |
| _ReqPromAdh Target | KPI-INBOUND-PO | 0.90 |
| _StockoutFG Target | KPI-STOCKOUT-FG | 0.02 |
| _StockoutIng Target | KPI-STOCKOUT-ING | 0.02 |
