# D02 Session Learnings

## PeriodSelection Values
- "YTD", "MTD", "MTO (Rolling 12)" — NOT just "MTO"

## Delta Period Comparison
Prior period uses SAME month/day as today, previous year:
`_priEnd = DATE(YEAR(_today)-1, MONTH(_today), DAY(_today))`

## Period Measure Pattern
Use inline VARs with SELECTEDVALUE(PeriodSelection[PeriodName]). Do NOT reference shared period measures inside VARs — they inherit wrong context.

| Period | Current Start | Prior End |
|--------|--------------|-----------|
| YTD | Jan 1 | DATE(YEAR-1, MONTH, DAY) |
| MTD | 1st of month | DATE(YEAR-1, MONTH, DAY) |
| MTO | EDATE(-12) | EDATE(-12) |

## Per-KPI Date Columns
- OTIF/OnTime/FillRate: SalesLine_Union[ShipmentDate]
- Stockout: DailyInventorySnapshot[SnapshotDate]
- ReqPromAdh: SalesHeader_Union[PostingDate]

## Power Query UNION Type Enforcement
After Table.Combine, add Table.TransformColumnTypes for:
Quantity/QuantityShipped -> type number
ShipmentDate/PromisedDeliveryDate/RequestedDeliveryDate -> type date
LineNo -> Int64.Type
DocumentNo/SourcePeriod -> type text

## KPIConfig Values
"OTIF %", "On-Time Shipment %", "Fill Rate %", "Stockout Rate FG %", "Stockout Rate Ingredients %", "Inbound PO Adherence %"

## TMSL Rules
1. Zero comments
2. Multi-line DAX: triple backticks
3. _Measures table must exist first

## Naming
_KPI_Total, _Var, _Base, _Value, _Target, _LatestMonth, _Period, _Period_Prior, _Delta, _Delta_Label, _Chip_Color, _Chip_BG_Color