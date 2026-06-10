# D02 KPI Measure Patterns — Session 2026-06-09

## D07 V5 AVERAGEX Pattern (DEPLOYED)

All 6 D02 KPIs now use the D07 `_InvInteg Accuracy %` shape:

```dax
_KPI_Value =
VAR _max_date   = CALCULATE(MAX(FactTable[DateCol]), ALL(FactTable))
VAR _cur_year   = YEAR(_max_date)
VAR _cur_month  = MONTH(_max_date)
VAR _inicio_mto = EDATE(_max_date, -12)
VAR _sel        = SELECTEDVALUE('Axis Period'[Axis Period Order])

VAR _acc_mtd =
    CALCULATE(
        AVERAGEX(FactTable, FactTable[FlagColumn]),
        FILTER(ALL(FactTable[DateCol]),
            YEAR(FactTable[DateCol])  = _cur_year &&
            MONTH(FactTable[DateCol]) = _cur_month))

VAR _acc_ytd =
    CALCULATE(
        AVERAGEX(FactTable, FactTable[FlagColumn]),
        FILTER(ALL(FactTable[DateCol]),
            YEAR(FactTable[DateCol])  = _cur_year))

VAR _acc_mto =
    CALCULATE(
        AVERAGEX(FactTable, FactTable[FlagColumn]),
        FILTER(ALL(FactTable[DateCol]),
            FactTable[DateCol] >= _inicio_mto &&
            FactTable[DateCol] <= _max_date))

RETURN SWITCH(_sel, 0, _acc_mtd, 1, _acc_ytd, 2, _acc_mto, _acc_mtd)
```

## Per-KPI Column Mapping

| KPI | FactTable | FlagColumn | DateCol | Base Measure |
|-----|-----------|------------|---------|-------------|
| OTIF | v_D02_OTIF_Daily | IsOTIFCompliant | ShipmentDate | DIVIDE(SUM(Compliant), SUM(Eligible)) |
| OnTime | v_D02_OnTime_Daily | IsOnTimeCompliant | ShipmentDate | DIVIDE(SUM(Compliant), SUM(Eligible)) |
| FillRate | v_D02_FillRate_Daily | — | ShipmentDate | DIVIDE(SUM(FillQty), SUM(Qty)) |
| ReqPromAdh | v_D02_ReqPromAdh_Daily | IsAdherent | PostingDate | DIVIDE(SUM(Adherent), SUM(Eligible)) |
| StockoutFG | v_D02_Stockout_Daily | — | SnapshotDate | DIVIDE(SUM(IsFGStockout), SUM(IsFG)) |
| StockoutIng | v_D02_Stockout_Daily | — | SnapshotDate | DIVIDE(SUM(IsRawStockout), SUM(IsRaw)) |

For ratio KPIs (FillRate, StockoutFG, StockoutIng), replace AVERAGEX(view, view[Flag]) with the full DIVIDE(SUM(num), SUM(denom), BLANK()) inside CALCULATE.

## What Broke in Earlier Attempts

1. AVERAGEX(FILTER(VALUES(DateCol), ...), [_Base]) — VALUES row context doesn't filter fact table, all periods return same value
2. _has_date_filter && gate on YTD/MTO — kills measure on plain card with no Date slicer
3. COALESCE(SELECTEDVALUE(...), 0) — unnecessary, SWITCH fallback handles NULL
4. CALCULATE([_Base], FILTER(...)) for ratio measures — context transition issue

## NULL PromisedDeliveryDate Business Rule (deployed 2026-06-09)

Applied to OTIF and On-Time SQL views:
- NULL PromisedDate → on-time by default
- OTIF still enforces In-Full (QuantityShipped >= Quantity)
- Late flag only fires when both dates exist AND ShipmentDate > PromisedDate
- ReqPromAdh unchanged (NULL = excluded, adherence meaningless without promise)

Impact: OTIF eligible 52K → 192K rows (3.6x). OTIF% 36.4% → 34.3%. On-Time% 97.7% → 99.4%.

## Item Category Hierarchy Enrichment (deployed 2026-06-09)

All sales-related D02 views include ItemCategoryName + ItemParentCategory:
- SalesLine_Union: LEFT JOIN bc.ItemCategory ic ON al.ItemCategoryCode = ic.Code
- Stockout: DailyInventorySnapshot → bc.Item → bc.ItemCategory (via ItemNo)
- Coverage: 99.8% SalesLine_Union, 99.9% Stockout
- COALESCE(NULLIF(ParentCategory, ''), Code) fallback ensures every row has a parent group
