# D02 Merged _Value + Period-Aware _Line Measures

> Added: 2026-06-09 | Context: D02 Service & Fulfillment OTIF refactor
> Source: `D02_Service_Fulfillment/TMDL/v_D02_OTIF_Measures.tmsl` (lines 10-31, 86-101)

## Problem Statement (Session 2026-06-09)

User reported OTIF KPI card showed a **flat fixed value** — never reacted to the Axis Period slicer (MTD/YTD/MTO). Root cause: the split architecture had `_OTIF Value = [_OTIF Base]` (pass-through) while `_OTIF Period` contained the actual SWITCH logic. The card visual referenced `_OTIF Value`, which had no period awareness.

Separate issue: line chart with `Date[Date]` on x-axis showed all historical data regardless of Axis Period selection. Plain `USERELATIONSHIP` did not filter to the selected window.

## Solution: Merged Architecture

1. **Move the SWITCH logic INTO `_OTIF Value`** — makes the card self-contained.
2. **Make `_OTIF Period` an alias** — `[_OTIF_Period] = [_OTIF Value]`. Avoids confusion.
3. **Add window filter to `_OTIF Line`** — `IF(_in_window, _base, BLANK())`.

## Verified `'_OTIF Value'` (Merged Switch Logic)

```dax
'_OTIF Value' =
    VAR _sel        = COALESCE(SELECTEDVALUE('Axis Period'[Axis Period Order]), 0)
    VAR _max_date   = CALCULATE(MAX(v_D02_OTIF_Daily[ShipmentDate]), ALL(v_D02_OTIF_Daily))
    VAR _cur_year   = YEAR(_max_date)
    VAR _cur_month  = MONTH(_max_date)
    VAR _inicio_mto = EDATE(_max_date, -12)
    VAR _has_date_filter = ISFILTERED('Date'[Date])
    VAR _ctx_year   = IF(_has_date_filter, YEAR(MIN('Date'[Date])), _cur_year)
    VAR _ctx_month  = IF(_has_date_filter, MONTH(MIN('Date'[Date])), _cur_month)
    VAR _ctx_first_day  = DATE(_ctx_year, _ctx_month, 1)
    VAR _ctx_last_day   = EOMONTH(_ctx_first_day, 0)

    VAR _mtd = CALCULATE([_OTIF Base],
        FILTER(ALL(v_D02_OTIF_Daily[ShipmentDate]),
            YEAR(v_D02_OTIF_Daily[ShipmentDate]) = _cur_year &&
            MONTH(v_D02_OTIF_Daily[ShipmentDate]) = _cur_month &&
            v_D02_OTIF_Daily[ShipmentDate] <= _max_date))

    VAR _ytd = IF(_has_date_filter && _ctx_year = _cur_year,
        CALCULATE([_OTIF Base]))

    VAR _mto = IF(_has_date_filter,
        IF(_ctx_first_day >= _inicio_mto && _ctx_last_day <= _max_date,
            CALCULATE([_OTIF Base])))

    RETURN SWITCH(_sel, 0, _mtd, 1, _ytd, 2, _mto, _mtd)
```

## Verified `'_OTIF Line'` (Period-Aware)

```dax
'_OTIF Line' =
    VAR _sel        = COALESCE(SELECTEDVALUE('Axis Period'[Axis Period Order]), 0)
    VAR _max_date   = CALCULATE(MAX(v_D02_OTIF_Daily[ShipmentDate]), ALL(v_D02_OTIF_Daily))
    VAR _cur_year   = YEAR(_max_date)
    VAR _cur_month  = MONTH(_max_date)
    VAR _inicio_mto = EDATE(_max_date, -12)
    VAR _base       = CALCULATE([_OTIF Base], USERELATIONSHIP(v_D02_OTIF_Daily[ShipmentDate], 'Date'[Date]))
    VAR _this_date  = MAX('Date'[Date])
    VAR _in_window  = SWITCH(TRUE(),
        _sel = 0, YEAR(_this_date) = _cur_year && MONTH(_this_date) = _cur_month && _this_date <= _max_date,
        _sel = 1, YEAR(_this_date) = _cur_year && _this_date <= _max_date,
        _sel = 2, _this_date >= _inicio_mto && _this_date <= _max_date,
        FALSE()
    )
    RETURN IF(_in_window, _base, BLANK())
```

## Downstream Measures That Reference The Merged `_Value`

```dax
'_OTIF Period' = [_OTIF Value]

'_OTIF Delta' =
    VAR _cur = [_OTIF Value]
    VAR _pri = [_OTIF Period Prior]
    RETURN IF(NOT ISBLANK(_cur) && NOT ISBLANK(_pri), _cur - _pri, BLANK())

'_OTIF Delta Label' =
    VAR _d = [_OTIF Delta]
    VAR _up = _d >= 0
    RETURN IF(ISBLANK(_d), "-- ", IF(_up, "▲ ", "▼ ") & FORMAT(ABS(_d), "0.0%"))

'_OTIF Chip Color' =
    VAR _d = [_OTIF Delta]
    RETURN IF(ISBLANK(_d), "#CCCCCC", IF(_d >= 0, "#027A48", "#B42318"))

'_OTIF Chip BG Color' =
    VAR _d = [_OTIF Delta]
    RETURN IF(ISBLANK(_d), "#FFFFFF", IF(_d >= 0, "#D1F2EB", "#FADBD8"))
```

## Replication Checklist (for other KPIs)

When applying this pattern to OnTime, FillRate, ReqPromAdh, StockoutFG, StockoutIng:

1. **Find the KPI's date column:** ShipmentDate (OnTime/FillRate), PostingDate (ReqPromAdh), SnapshotDate (Stockout FG/Ing).
2. **Replace `v_D02_OTIF_Daily[ShipmentDate]`** with the correct `view[date_col]` throughout.
3. **Replace `[_OTIF Base]`** with `[_<KPI> Base]`.
4. **For stockout KPIs invert chip logic**: `delta <= 0` → green (lower is better).
5. **Update `displayFolder:`** to `D02\_<KPI>`.
6. **Verify `_Delta` still references `_Value`** (the merged measure), not the old `_Period` alias.
7. **Replicate the `_Line` window pattern** exactly — same `SWITCH(TRUE(), ...)` structure, just with the KPI's date column.

## Why Merging Matters

User mental model: "`_OTIF Value` on a card should respond to the Axis Period slicer."

Split architecture breaks this mental model because:
- Card references `_Value` (flat)
- Slicer changes `_Period` (hidden)
- User sees no effect, has to discover the `_Period` alias

Merged architecture matches D07's existing `_InvInteg Accuracy %` pattern which works. It also removes dead alias measures and simplifies downstream references (`_Delta` points to `_Value` which now contains the SWITCH).
