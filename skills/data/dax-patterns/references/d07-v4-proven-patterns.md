# D07 V4 Proven Patterns — Reference (2026-06-09)

These are the **confirmed working** DAX patterns from D07 Warehouse Operations V4 (`D07 Warehouse Operations_v4.tmdl`, 2948 lines). Use as the canonical template when writing any new KPI measures for Kings Pastry.

---

## Axis Period Calculated Table

```dax
'Axis Period' = {
    ("MTD", NAMEOF('Date'[Day Label]),     0),
    ("YTD", NAMEOF('Date'[Month Label]),   1),
    ("MTO", NAMEOF('Date'[Month Label MTO]), 2)
}
```

- **Used in**: Period slicer AND line chart X-axis (as `'Axis Period'[Axis Period Fields]`)
- MTD → daily grain (Day Label)
- YTD → monthly grain (Month Label)
- MTO → trailing 12 months (Month Label MTO)

---

## InvInteg Accuracy % (Full D07 Reference)

This is the **exact** measure from D07 V4 that the D02 period pattern must match.

```dax
_InvInteg Accuracy % = 
VAR _max_date   = CALCULATE(MAX(InvIntegrity[CountDate]), ALL(InvIntegrity))
VAR _cur_year   = YEAR(_max_date)
VAR _cur_month  = MONTH(_max_date)
VAR _inicio_mto = EDATE(_max_date, -12)
VAR _sel        = SELECTEDVALUE('Axis Period'[Axis Period Order])

VAR _ctx_year      = YEAR(MIN('Date'[Date]))
VAR _ctx_month     = MONTH(MIN('Date'[Date]))
VAR _ctx_first_day = DATE(_ctx_year, _ctx_month, 1)
VAR _ctx_last_day  = EOMONTH(_ctx_first_day, 0)

VAR _acc_mtd =
    CALCULATE(
        AVERAGEX(InvIntegrity, InvIntegrity[RecordAccuracyPct]),
        FILTER(ALL(InvIntegrity[CountDate]),
            YEAR(InvIntegrity[CountDate])  = _cur_year &&
            MONTH(InvIntegrity[CountDate]) = _cur_month))

VAR _acc_ytd =
    IF(_ctx_year = _cur_year,
        CALCULATE(AVERAGEX(InvIntegrity, InvIntegrity[RecordAccuracyPct])))

VAR _acc_mto =
    IF(_ctx_first_day >= _inicio_mto && _ctx_last_day <= _max_date,
        CALCULATE(AVERAGEX(InvIntegrity, InvIntegrity[RecordAccuracyPct])))

RETURN SWITCH(_sel, 0, _acc_mtd, 1, _acc_ytd, 2, _acc_mto)
```

**Key structural features (all mandatory in D02 port):**
1. `CALCULATE(MAX(view[date]), ALL(view))` — date derived from data, not TODAY()
2. Plain `SELECTEDVALUE` — NO COALESCE wrapper
3. MTD uses `FILTER(ALL(view[date]))` with explicit YEAR/MONTH match
4. YTD uses `IF(_ctx_year = _cur_year, ...)` — no DATESYTD
5. MTO uses range check against `_inicio_mto`..`_max_date`
6. SWITCH fallback value is omitted (BLANK) — no default `_mtd`

---

## D02 Port Checklist (What Must Match D07 V4)

| Feature | D07 V4 Pattern | D02 Must Use |
|---------|---------------|--------------|
| `_sel` | `SELECTEDVALUE(...)` | `SELECTEDVALUE(...)` (NO COALESCE) |
| `_cur_year` | `YEAR(CALCULATE(MAX(view[date]), ALL(view)))` | Same |
| MTD | `FILTER(ALL(view[date]), YEAR= && MONTH=)` | Same |
| YTD | `IF(_ctx_year = _cur_year, CALCULATE([_Base]))` | Same (NO DATESYTD) |
| MTO | `IF(range_check, CALCULATE([_Base]))` | Same (NO DATEADD) |
| Prior YTD | `FILTER(ALL(view[date]), YEAR = _cur_year - 1)` | Same (NO SAMEPERIODLASTYEAR) |
| Prior MTO | `FILTER(ALL(view[date]), date >= py_inicio && date <= py_max)` | Same |
| SWITCH default | No default (BLANK) | Use `_mtd` as fallback |

---

## TMSL File Structure (`example.tmsl` / `D02_All_Measures_Script.tmsl`)

The single authoritative file format for the TMDL view. Structure:

```
createOrReplace
\tref table _Measures
\t\tmeasure '_OTIF Base' =
\t\t\t\tVAR _x = 1
\t\t\t\tRETURN _x
\t\t\tdisplayFolder: D02\_OTIF

\t\tmeasure '_OTIF Value' = [_OTIF Base]
\t\t\tdisplayFolder: D02\_OTIF
```

**Rules (enforced in D07 V4):**
- ZERO comments anywhere
- TABs only (no spaces)
- `createOrReplace` at column 0
- `ref table _Measures` at 1 tab
- `measure 'Name' =` at 2 tabs
- Multi-line DAX body at 4 tabs
- `displayFolder:` at 3 tabs
- Blank line between measures
