---
name: dax-patterns
description: "DAX measure writing patterns for Kings Pastry Power BI dashboards. Covers common pitfalls (NOT BLANK vs NOT ISBLANK, table naming, composite keys), measure templates (D07-style _Total/_Var/_Base pattern), and data exploration before building. CORRECTED 2026-06-09: Period measures use FILTER(ALL=view[date])) only — no COALESCE, no ISFILTERED, no DATESYTD, no DATEADD. Axis Period Field Parameter drives both slicer AND x-axis. Load when writing DAX measures for any KP dashboard."
version: 1.5.0
author: OWL
platforms: [macos]
metadata:
  hermes:
    tags: [dax, power-bi, kpi, measures, patterns]
    related_skills: [writing-plans, build-dashboard]
---

# DAX Patterns — Kings Pastry Power BI

## Common DAX Errors

### NOT BLANK() is invalid
**Wrong:** `NOT BLANK(SalesLine[ShipmentDate])`
**Right:** `NOT ISBLANK(SalesLine[ShipmentDate])`

`BLANK()` takes zero arguments. `ISBLANK()` checks if a value is blank.

### Table names in DAX ≠ SQL names
SQL: `bc.SalesLine`, `pbi.DailyInventorySnapshot`
Power BI / DAX: `SalesLine`, `DailyInventorySnapshot` (no schema prefix)

Always use the Power BI table name in DAX.

### Composite key tables: MAX() not SELECTEDVALUE()
Tables with composite keys (e.g., Axis Period) fail with SELECTEDVALUE:
"Column [Axis Period] is part of composite key, but not all columns of the composite key are included in the expression or its dependent expression."

**Wrong:** `SELECTEDVALUE('Axis Period'[Axis Period], "YTD")`
**Right:** `MAX('Axis Period'[Axis Period])`

### FILTER(ALL('Date')) overrides relationships
`FILTER(ALL('Date'), ...)` removes ALL filters including active relationships.

**Wrong:**
```dax
CALCULATE([Measure], FILTER(ALL('Date'), 'Date'[Date] >= _start && 'Date'[Date] <= _end))
```

**Right — filter fact table directly:**
```dax
CALCULATE([Measure], FactTable[DateColumn] >= _start && FactTable[DateColumn] <= _end)
```

**Right — use DATESBETWEEN (preserves relationship):**
```dax
CALCULATE([Measure], DATESBETWEEN('Date'[Date], _start, _end))
```

## KPI Measure Pattern (D07-style)

```dax
_KPI_Total      — denominator (all eligible records)
_KPI_Var        — "bad" records (failures)
_KPI_Base       — DIVIDE(Total - Var, Total)
_KPI_Value      — PERIOD-AWARE card measure (contains SWITCH logic — NOT a pass-through)
_KPI_Period     — alias: [_KPI_Value] (kept for backward compat)
_KPI_Target     — KPIConfig lookup (TargetMonth where KPIName = "X")
_KPI_Delta      — Period vs Period Prior (same timeframe, 1 year back)
_KPI_Delta_Label — "▲ 1.2%"
_KPI_Chip_Color — green/red based on goal direction
_KPI_Line       — PERIOD-AWARE line chart measure (USERELATIONSHIP + window filter)
```

### Architecture: Merged SWITCH into _Value (Hernan preference — 2026-06-09)

**CRITICAL.** The user explicitly prefers the **merged** architecture: `_KPI_Value` contains the full SWITCH-on-Axis-Period logic so it works as both:
1. A card value that reacts to the Axis Period slicer (MTD / YTD / MTO)
2. A "single smart measure" per KPI that doesn't require knowing internal splits

**❌ WRONG (split architecture — causes slicer disconnect):**
```dax
_KPI_Value = [_KPI_Base]                  // plain pass-through
_KPI_Period = VAR _sel = ... SWITCH(...)  // SWITCH in separate measure
```
Card uses `_KPI_Value` → slicer does nothing because `_KPI_Base` has no period logic.

**✅ RIGHT (merged architecture):**
```dax
_KPI_Value = 
    VAR _sel = ...
    VAR _mtd = ...
    VAR _ytd = ...
    VAR _mto = ...
    RETURN SWITCH(_sel, 0, _mtd, 1, _ytd, 2, _mto, _mtd)
_KPI_Period = [_KPI_Value]                 // alias, optional
_KPI_Delta = [_KPI_Value] - [_KPI_Period_Prior]   // references the merged measure
```

**Why this matters:** Line charts and cards on the same page share one visual model. When `_Value` and the slicer are "decoupled" by a split architecture, the user sees a flat, unresponsive card and has to discover a hidden `_Period` alias. Merging eliminates that UX surprise and matches the D07 `_InvInteg Accuracy %` pattern that already works.

## Data Exploration Before Building

Before writing measures, run these checks:

```dax
-- Row count and date range
EVALUATE ROW("Count", COUNTROWS(Table), "MinDate", MIN(Table[Date]), "MaxDate", MAX(Table[Date]))

-- Field population
EVALUATE ROW("WithDate", CALCULATE(COUNTROWS(Table), NOT ISBLANK(Table[Date])), "Total", COUNTROWS(Table))

-- Category values
EVALUATE SUMMARIZE(Table, Table[Category], "Count", COUNTROWS(Table))
```

## SQL View-First Methodology (D07 V3 Pattern)

Create SQL views in Azure that pre-calculate KPI flags at daily grain. PBI imports simple tables; DAX only handles period logic. See `references/sql-view-first-methodology.md` for full details.

### Slicer Key Requirements (CRITICAL for Chart Filtering)
**ALL daily KPI views** (`v_D02_OTIF_Daily`, `v_D02_OnTime_Daily`, `v_D02_FillRate_Daily`, `v_D02_ReqPromAdh_Daily`) **MUST** include the following columns to enable Channel and Region slicer filtering on line charts and detail tables:
- `SelltoCustomerNo` (joined from header)
- `ShipToCounty` (joined from header)
- `ShipToCountryRegionCode` (joined from header)
- `RegionKey` (calculated as: `ISNULL(ShipToCountryRegionCode, '') + '|' + ISNULL(ShipToCounty, '')`)

Without these columns, the fact table has no relationship path to `scm.CustomerSales` or `scm.CountryZonesMapping`, causing slicers to silently fail on visual-level aggregations.

### Date Column Mapping (CRITICAL)
Each KPI view outputs a **different date column**. TMDL measures MUST reference the correct one:
- OTIF/OnTime/FillRate: `View[ShipmentDate]` ✅
- ReqPromAdh: `View[PostingDate]` ✅ (NOT ShipmentDate)
- Stockout: `View[SnapshotDate]` ✅ (NOT ShipmentDate)

**Most common TMDL error:** Copy-pasting `_Period`/`_Line` measures from OTIF without changing `[ShipmentDate]` to the correct date column. Always audit view column names against DAX references.

### pyodbc CREATE VIEW Pattern
pyodbc `execute()` allows only one statement. `CREATE VIEW` must be FIRST.
```python
cursor.execute("DROP VIEW IF EXISTS pbi.v_X")  # Step 1: separate execute
conn.commit()
cursor.execute("CREATE VIEW pbi.v_X AS ...")    # Step 2: CREATE VIEW
conn.commit()
```
Use `[LineNo]` (brackets) for reserved words in pyodbc SQL strings.

## Period Measure Pattern (D07 V4 Proven — CORRECTED 2026-06-09)

**Source of truth:** D07 V4 `_InvInteg Accuracy %`, `example.tmsl`. This pattern uses **FILTER(ALL(view[date])) only** — no DATESYTD, no DATEADD, no ISFILTERED. This is the pattern that works correctly with the `'Axis Period'[Axis Period Fields]` field parameter on the chart X-axis.

## D02 KPI Measure Patterns — AVERAGEX + Last Year Line + Variance (2026-06-09)

### _Value Measure — D07 AVERAGEX Pattern (confirmed working)

Replaces old `CALCULATE([_Base], FILTER(ALL(date)))`. Uses `AVERAGEX(table, column)` inside `CALCULATE` with `FILTER(ALL(date))`:

```dax
_OTIF_Value =
VAR _max_date   = CALCULATE(MAX(v_D02_OTIF_Daily[ShipmentDate]), ALL(v_D02_OTIF_Daily))
VAR _cur_year   = YEAR(_max_date)
VAR _cur_month  = MONTH(_max_date)
VAR _inicio_mto = EDATE(_max_date, -12)
VAR _sel        = SELECTEDVALUE('Axis Period'[Axis Period Order])
VAR _acc_mtd = CALCULATE(AVERAGEX(v_D02_OTIF_Daily, v_D02_OTIF_Daily[IsOTIFCompliant]), FILTER(ALL(v_D02_OTIF_Daily[ShipmentDate]), YEAR(v_D02_OTIF_Daily[ShipmentDate]) = _cur_year && MONTH(v_D02_OTIF_Daily[ShipmentDate]) = _cur_month))
VAR _acc_ytd = CALCULATE(AVERAGEX(v_D02_OTIF_Daily, v_D02_OTIF_Daily[IsOTIFCompliant]), FILTER(ALL(v_D02_OTIF_Daily[ShipmentDate]), YEAR(v_D02_OTIF_Daily[ShipmentDate]) = _cur_year))
VAR _acc_mto = CALCULATE(AVERAGEX(v_D02_OTIF_Daily, v_D02_OTIF_Daily[IsOTIFCompliant]), FILTER(ALL(v_D02_OTIF_Daily[ShipmentDate]), v_D02_OTIF_Daily[ShipmentDate] >= _inicio_mto && v_D02_OTIF_Daily[ShipmentDate] <= _max_date))
RETURN SWITCH(_sel, 0, _acc_mtd, 1, _acc_ytd, 2, _acc_mto, _acc_mtd)
```

### _Line Last Year Measure (USERELATIONSHIP overlay)

Shows last year's daily trend on current X-axis. For ratio-based KPIs (FillRate, Stockout) use `DIVIDE(SUM(numerator), SUM(denominator))` instead of `AVERAGEX`:
```dax
_OTIF_Line_Last_Year =
VAR _last_year = YEAR(CALCULATE(MAX(v_D02_OTIF_Daily[ShipmentDate]), ALL(v_D02_OTIF_Daily))) - 1
RETURN CALCULATE(AVERAGEX(v_D02_OTIF_Daily, v_D02_OTIF_Daily[IsOTIFCompliant]), FILTER(ALL(v_D02_OTIF_Daily[ShipmentDate]), YEAR(v_D02_OTIF_Daily[ShipmentDate]) = _last_year), USERELATIONSHIP(v_D02_OTIF_Daily[ShipmentDate], 'Date'[Date]))
```

### _Variance Measure
```dax
_OTIF_Variance = VAR _actual = [_OTIF_Value] VAR _target = [_OTIF_Target] RETURN IF(NOT ISBLANK(_actual) && NOT ISBLANK(_target), _actual - _target, BLANK())
```

### Per-KPI Column Mapping (CRITICAL — always verify)

| KPI | View | Date Column | Value Column |
|-----|------|-------------|--------------|
| OTIF | v_D02_OTIF_Daily | ShipmentDate | AVERAGEX(IsOTIFCompliant) |
| OnTime | v_D02_OnTime_Daily | ShipmentDate | AVERAGEX(IsOnTimeCompliant) |
| FillRate | v_D02_FillRate_Daily | ShipmentDate | DIVIDE(SUM(FillQuantity), SUM(Quantity)) |
| ReqPromAdh | v_D02_ReqPromAdh_Daily | **PostingDate** | AVERAGEX(IsAdherent) |
| StockoutFG | v_D02_Stockout_Daily | **SnapshotDate** | DIVIDE(SUM(IsFGStockout), SUM(IsFG)) |
| StockoutIng | v_D02_Stockout_Daily | **SnapshotDate** | DIVIDE(SUM(IsRawStockout), SUM(IsRaw)) |

Batch-apply to all 6 KPIs after OTIF validation. User preference: one pass, one commit.

## NULL PromisedDeliveryDate Business Rule (2026-06-09)

For OTIF and On-Time: NULL PromisedDeliveryDate → treat as on-time. In-Full still enforced for OTIF.
For ReqPromAdh: keep excluded (adherence meaningless without both dates).
SQL CASE: `WHEN ... AND (PromisedDeliveryDate IS NULL OR ShipmentDate <= PromisedDeliveryDate) THEN 1`

```dax
_KPI_Period =
VAR _max_date   = CALCULATE(MAX(FactTable[DateCol]), ALL(FactTable))
VAR _cur_year   = YEAR(_max_date)
VAR _cur_month  = MONTH(_max_date)
VAR _inicio_mto = EDATE(_max_date, -12)
VAR _sel        = SELECTEDVALUE('Axis Period'[Axis Period Order])

VAR _ctx_year      = YEAR(MIN('Date'[Date]))
VAR _ctx_month     = MONTH(MIN('Date'[Date]))
VAR _ctx_first_day = DATE(_ctx_year, _ctx_month, 1)
VAR _ctx_last_day  = EOMONTH(_ctx_first_day, 0)

VAR _mtd = CALCULATE([_KPI_Base],
    FILTER(ALL(FactTable[DateCol]),
        YEAR(FactTable[DateCol])  = _cur_year &&
        MONTH(FactTable[DateCol]) = _cur_month))

VAR _ytd = IF(_ctx_year = _cur_year,
    CALCULATE([_KPI_Base]))

VAR _mto = IF(_ctx_first_day >= _inicio_mto && _ctx_last_day <= _max_date,
    CALCULATE([_KPI_Base]))

RETURN SWITCH(_sel, 0, _mtd, 1, _ytd, 2, _mto, _mtd)
```

```dax
_KPI_Period_Prior =
VAR _max_date   = CALCULATE(MAX(FactTable[DateCol]), ALL(FactTable))
VAR _cur_year   = YEAR(_max_date)
VAR _cur_month  = MONTH(_max_date)
VAR _inicio_mto = EDATE(_max_date, -12)
VAR _py_inicio  = EDATE(_inicio_mto, -12)
VAR _py_max     = EDATE(_max_date, -12)
VAR _sel        = SELECTEDVALUE('Axis Period'[Axis Period Order])

VAR _mtd_p = CALCULATE([_KPI_Base],
    FILTER(ALL(FactTable[DateCol]),
        YEAR(FactTable[DateCol])  = _cur_year - 1 &&
        MONTH(FactTable[DateCol]) = _cur_month))

VAR _ytd_p = CALCULATE([_KPI_Base],
    FILTER(ALL(FactTable[DateCol]),
        YEAR(FactTable[DateCol]) = _cur_year - 1))

VAR _mto_p = CALCULATE([_KPI_Base],
    FILTER(ALL(FactTable[DateCol]),
        FactTable[DateCol] >= _py_inicio &&
        FactTable[DateCol] <= _py_max))

RETURN SWITCH(_sel, 0, _mtd_p, 1, _ytd_p, 2, _mto_p, _mtd_p)
```

**CRITICAL RULES:**
1. **NO COALESCE** — use plain `SELECTEDVALUE`. The default fallback `_mtd` in the SWITCH already handles NULL slicer selection.
2. **NO ISFILTERED, NO DATESYTD, NO DATEADD** — these time-intelligence functions fight with the `'Axis Period'[Axis Period Fields]` field parameter on the X-axis, causing the chart to show a flat line. Use only `FILTER(ALL(view[date]))` for explicit date range filtering.
3. **`_cur_year`/`_cur_month` derived from data, not TODAY()** — `CALCULATE(MAX(view[date]), ALL(view))` is the source of truth. This prevents "2022-01-01" fallback bugs when data is fresher than the date table.
4. **Per-KPI date columns**: Each KPI filters on its own date column:
   - OTIF/OnTime/FillRate: `[ShipmentDate]`
   - Stockout FG/Ing: `[SnapshotDate]`
   - ReqPromAdh: `[PostingDate]`
5. **SWITCH default = _mtd** — if slicer is blank or value doesn't match, fallback to MTD.

## Axis Period Field Parameter (X-Axis Driver)

**This is what makes the chart dynamic per period.** The `'Axis Period'` table is a Power BI Field Parameter (calculated table) that dynamically swaps the X-axis column:

| Slicer Selection | Order | X-Axis Column | Grain |
|-----------------|-------|---------------|-------|
| MTD | 0 | `'Date'[Day Label]` | Daily |
| YTD | 1 | `'Date'[Month Label]` | Monthly |
| MTO | 2 | `'Date'[Month Label MTO]` | Monthly trailing |

**Calculated table definition:**
```dax
'Axis Period' = {
    ("MTD", NAMEOF('Date'[Day Label]),     0),
    ("YTD", NAMEOF('Date'[Month Label]),   1),
    ("MTO", NAMEOF('Date'[Month Label MTO]), 2)
}
```

**Line Chart X-Axis:** `'Axis Period'[Axis Period Fields]` — NOT `Date[Date]`. This is the entire point of the field parameter: MTD shows daily, YTD shows monthly, MTO shows trailing months.

**Period Slicer:** `'Axis Period'[Axis Period]` (MTD / YTD / MTO)

The Axis Period table must exist in the model before any `_Period` measures are created. TMSL: `Axis_Period_Table.tmsl` in `TabularEditor/`.

## Line Measure Pattern (USERELATIONSHIP + Period Window Filter)

Line charts with `Date[Date]` on the X-axis need TWO things:
1. `USERELATIONSHIP` so the X-axis filter flows to the fact table's date column
2. A **window filter** (`_in_window`) that returns `BLANK()` for dates outside the selected Axis Period, hiding them from the chart

Plain `USERELATIONSHIP` alone shows ALL daily data regardless of the Axis Period slicer — the user sees a 5-year line even when MTD is selected.

### Simple form (when no Axis Period slicer interaction is needed)
```dax
_KPI_Line =
    CALCULATE([_KPI_Base], USERELATIONSHIP(FactTable[DateCol], 'Date'[Date]))
```

### Period-aware form (when line chart MUST respect Axis Period slicer)
```dax
_KPI_Line =
    VAR _sel        = COALESCE(SELECTEDVALUE('Axis Period'[Axis Period Order]), 0)
    VAR _max_date   = CALCULATE(MAX(FactTable[DateCol]), ALL(FactTable))
    VAR _cur_year   = YEAR(_max_date)
    VAR _cur_month  = MONTH(_max_date)
    VAR _inicio_mto = EDATE(_max_date, -12)
    VAR _base       = CALCULATE([_KPI_Base], USERELATIONSHIP(FactTable[DateCol], 'Date'[Date]))
    VAR _this_date  = MAX('Date'[Date])
    VAR _in_window  = SWITCH(TRUE(),
        _sel = 0, YEAR(_this_date) = _cur_year && MONTH(_this_date) = _cur_month && _this_date <= _max_date,
        _sel = 1, YEAR(_this_date) = _cur_year && _this_date <= _max_date,
        _sel = 2, _this_date >= _inicio_mto && _this_date <= _max_date,
        FALSE()
    )
    RETURN IF(_in_window, _base, BLANK())
```

**Key details:**
- `_base` still uses `USERELATIONSHIP` so the X-axis filter flows
- `_this_date = MAX('Date'[Date])` gets the current X-axis point
- `_in_window` is a boolean gate that matches the selected Axis Period window
- `BLANK()` on out-of-window dates causes the chart to suppress those points
- `COALESCE` here is OK because the measure is used on a chart (not a card), and `_sel = 0` default still maps to MTD

For LY-only overlay series on the same chart:
```dax
_KPI_Line_LY =
    VAR _last_year = YEAR(MAX(OtherFactTable[DateCol]))
    RETURN CALCULATE(
        [_KPI_Base],
        YEAR(OtherFactTable[DateCol]) = _last_year,
        USERELATIONSHIP(OtherFactTable[DateCol], 'Date'[Date])
    )
```

## Target Measure Pattern (Robust)

```dax
_KPI_Target =
CALCULATE(
    SELECTEDVALUE(KPIConfig[TargetMonth]),
    KPIConfig[KPIID] = "KPI-OTIF"  -- canonical ID, NOT dashboard-prefixed
)
```

**CRITICAL:** Use canonical `KPIConfig[KPIID]` (e.g., `"KPI-OTIF"`, `"KPI-FILLRATE"`, `"KPI-STOCKOUT-FG"`). These are SHARED across dashboards (D, D02, D05, D07). Never invent IDs — query the table: `SELECT KPIID, KPIName, TargetMonth, Dashboard FROM pbi.KPIConfig`. The `Dashboard` column is the dimension filter, not part of the ID.

Note: TargetMonth is a decimal (0.95 = 95%). Multiply by 100 if displaying as whole number percentage.

## Chip Color Pattern (D07 Palette)

Higher is better (e.g., OTIF, Fill Rate):
```dax
_KPI_Chip_Color = 
    VAR _d = [_KPI_Delta]
    RETURN IF(ISBLANK(_d), "#CCCCCC", IF(_d >= 0, "#027A48", "#B42318"))

_KPI_Chip_BG_Color = 
    VAR _d = [_KPI_Delta]
    RETURN IF(ISBLANK(_d), "#FFFFFF", IF(_d >= 0, "#D1F2EB", "#FADBD8"))
```

Lower is better (inverted — e.g., Stockout FG/Ing):
```dax
_KPI_Chip_Color = 
    VAR _d = [_KPI_Delta]
    RETURN IF(ISBLANK(_d), "#CCCCCC", IF(_d <= 0, "#027A48", "#B42318"))

_KPI_Chip_BG_Color = 
    VAR _d = [_KPI_Delta]
    RETURN IF(ISBLANK(_d), "#FFFFFF", IF(_d <= 0, "#D1F2EB", "#FADBD8"))
```

**Stockout Delta Label** — the `_up` variable determines arrow direction. For "lower is better" KPIs, negative delta = improvement:
```dax
_KPI_Delta_Label =
    VAR _d = [_KPI_Delta]
    VAR _up = _d <= 0  // Lower is better: negative delta = improvement = ▲
    RETURN IF(ISBLANK(_d), "-- ", IF(_up, "▲ ", "▼ ") & FORMAT(ABS(_d), "0.0%"))
```

**Common mistake:** Copy-pasting `_StockoutIng` or `_StockoutFG` with `_up = _d >= 0` (same as OTIF). This is WRONG — the arrow direction will be inverted.

## User Workflow Preference (Hernan)

Hernan prefers a step-by-step, measurable approach to DAX measure building:

1. **Explore first** - Run data exploration queries to understand row counts, date ranges, and field population
2. **Build base components** - Start with _Total (denominator), then _Var (numerator), then _Base (DIVIDE)
3. **Verify each step** - Test each measure in a card visual before proceeding to the next component
4. **Build display measures** - Add _Value (wrapper), _Target (KPIConfig lookup)
5. **Add time intelligence** - Build _Period, _Period_Prior, _Delta, _Delta_Label
6. **Finish with visuals** - Add _Chip_Color, _Chip_BG_Color for conditional formatting

This approach provides early feedback and catches issues before building complex measures.
Prefer concrete, copy-pasteable DAX code over abstract descriptions.
Value clear separation between data exploration and measure building steps.

## Live vs Archive Table Pattern (Kings Pastry Specific) — UPDATED 2026-06-06

**VERIFIED FINDINGS (2026-06-06):**
- Archive table column names use **PascalCase (NO underscores)** — identical to current tables
  - Archive: `DocumentType`, `ShipmentDate`, `RequestedDeliveryDate`, `PromisedDeliveryDate`
  - Current: `DocumentType`, `ShipmentDate`, `RequestedDeliveryDate`, `PromisedDeliveryDate`
  - ✅ Names are IDENTICAL — clean UNION possible without renaming
- Archive `SalesLineArchive[ShipmentDate]` is **99.96% populated** (388,102 / 388,267 rows)
  - This is the ACTUAL ship date, NOT planned — full OTIF history possible!
- Only **8 duplicate Document_No** values between current + archive — trivial dedup
- Archive `RequestedDeliveryDate` is only **24% populated** (header), **28%** (line)
- Archive `PromisedDeliveryDate` is only **22% populated** (header), **27%** (line)

**MERGE STRATEGY: Option A (UNION ALL with SourcePeriod flag)**
- Single fact table simplifies DAX measures and relationships
- Add `SourcePeriod` column: "Current" / "Archive" for filtering
- Dedup: prefer Current over Archive for 8 overlapping orders

**Implementation (Power Query M):**
```
SalesHeader_Union =
    let
        Current = Table.AddColumn(SalesHeader, "SourcePeriod", each "Current"),
        Archive = Table.AddColumn(SalesHeaderArchive, "SourcePeriod", each "Archive"),
        Combined = Table.Combine({Current, Archive}),
        CurrentDocNos = Table.Column(SalesHeader, "No"),
        Deduped = Table.SelectRows(Combined, each
            [SourcePeriod] = "Current" or not List.Contains(CurrentDocNos, [No])
        )
    in
        Deduped
```

**DAX table names (use these in measures):**
- `SalesHeader_Union` (not `bc_SalesHeader`)
- `SalesLine_Union` (not `bc_SalesLine`)
- `DailyInventorySnapshot` (not `pbi_DailyInventorySnapshot`)
- `KPIConfig` (not `pbi_KPIConfig`)

---

## Tabular Editor Script Format — UPDATED 2026-06-07 (v2)

### pyodbc CREATE VIEW Pattern (CRITICAL for Azure SQL automation)

pyodbc `execute()` only allows one statement per call. `CREATE VIEW` must be FIRST.

**WRONG** — fails with "must be first statement":
```python
cursor.execute("IF OBJECT_ID('pbi.v_X','V') IS NOT NULL DROP VIEW; CREATE VIEW ...")
```

**WRONG** — silently fails (view not created). `CREATE OR ALTER` requires the object to ALREADY exist:
```python
cursor.execute("CREATE OR ALTER VIEW pbi.v_X AS SELECT 1")  # Fails silently if view doesn't exist
```

**CORRECT** — two-step drop then create:
```python
cursor.execute("DROP VIEW IF EXISTS pbi.v_X")  # Step 1
conn.commit()
sql = re.sub(r'CREATE\s+OR\s+ALTER\s+VIEW', 'CREATE VIEW', sql, flags=re.IGNORECASE)  # Step 2
cursor.execute(sql)  # Step 3
conn.commit()
cursor.execute("SELECT COUNT(*) FROM pbi.v_X")  # Step 4 verify
```

Also: bracket reserved words in pyodbc SQL strings (e.g. `[LineNo]` not `LineNo`).

### TMDL Table Name Escaping (CRITICAL)

In TMDL files, backslash `\` is the display folder separator: `D02\_OTIF` = folder `D02`, subfolder `OTIF`.

**Table/view names must NEVER contain backslashes.** A reference like `v_D02\_FillRate_Daily` is WRONG — the `\_` makes it look like a folder path.

**Audit pattern** — search all TMDL files before executing:
```python
import re
bad = re.findall(r'v_D02\\[^\[]+', content)  # Finds v_D02\_XXX (wrong table name)
good = re.findall(r'v_D02_[a-zA-Z0-9_]+\[', content)  # Finds v_D02_XXX[column] (correct)
```

**Fix:** Replace `v_D02\_XXX_Daily` → `v_D02_XXX_Daily` (remove backslash from table name only, keep in displayFolder).

## TMDL Indentation Rules (CRITICAL — v3 2026-06-09)

**`displayFolder` at 3 tabs is MANDATORY.** This is the single most common TMDL error. If displayFolder is at any other indentation level, TE3 creates the measure but does NOT apply the display folder.

**Working pattern (from OTIF — confirmed in TE3):**
```
createOrReplace               ← col 0
\tref table _Measures          ← 1 tab
\t\tmeasure '_Name' =         ← 2 tabs
\t\t\t\tVAR _x = 1           ← 4 tabs (multi-line DAX body)
\t\t\t\tRETURN _x
\t\t\tdisplayFolder: D02\_F   ← 3 tabs (CRITICAL)

\t\tmeasure '_Val' = [_Name]  ← 2 tabs + DAX at 3 tabs
\t\t\tdisplayFolder: D02\_F   ← 3 tabs
```

**Anti-patterns that break displayFolder:**
- `^\t\t\tdisplayFolder` (2 tabs) — measure created, folder NOT applied
- `^\t\t    displayFolder` (2 tabs + 4 spaces) — parse error or ignored
- `^\t\t\t\tdisplayFolder` (4 tabs) — parse error

**Verification:** `head -8 file.tmdl | cat -et` — displayFolder lines MUST show exactly `^I^I^I` (3 tabs).

**Claude Code subagent warning:** Subagents frequently replace tabs with spaces. Always verify and fix indentation after any subagent TMDL work.

## TMDL Reconstruction & Validation Checklist

When regenerating a combined TMDL file (e.g., `v_D02_AllKPIs_Measures.tmdl`) from individual clean files, always apply this validation checklist before finalizing:

1. **Parentheses Balance**: Run a quick Python script to ensure open and close parentheses match exactly.
   ```python
   open_parens = content.count('(')
   close_parens = content.count(')')
   assert open_parens == close_parens, f"Unbalanced: {open_parens} open, {close_parens} close"
   ```
2. **Measure Count**: For 6 KPIs with 10 measures each (Base, Value, Target, Period, Period Prior, Delta, Delta Label, Chip Color, Chip BG Color, Line), verify exactly 60 measures are defined with zero duplicates.
   ```python
   import re
   measures = re.findall(r"measure '([^']+)'\\s*=", content)
   assert len(measures) == 60, f"Expected 60 measures, got {len(measures)}"
   assert len(measures) == len(set(measures)), "Duplicate measures detected"
   ```
3. **D07 V4 Period Pattern Applied**: Ensure ALL `_Period` measures use plain `SELECTEDVALUE('Axis Period'[Axis Period Order])` (NO COALESCE), `CALCULATE(MAX(view[date]), ALL(view))` for `_cur_year`, and `FILTER(ALL(view[date]))` for MTD — no DATESYTD, DATEADD, or ISFILTERED. See "Period Measure Pattern (D07 V4 Proven)" section for the canonical template.
4. **KPIID over KPIName**: Verify all `_Target` measures use `KPIConfig[KPIID] = "KPI-XXX"`. **CRITICAL (CORRECTED 2026-06-09):** KPIIDs are **canonical/shared across dashboards** — NOT dashboard-prefixed. The `Dashboard` column (`D`, `D02`, `D05`, `D07`) is a separate dimension. Validate against `pbi.KPIConfig`. Current verified mapping: OTIF=`KPI-OTIF` (95%, Dashboard=D), OnTime=`KPI-ONTIMESHIP` (90%, Dashboard=D), FillRate=`KPI-FILLRATE` (95%, Dashboard=D), ReqPromAdh=`KPI-INBOUND-PO` (90%, Dashboard=D05), StockoutFG=`KPI-STOCKOUT-FG` (2%, Dashboard=D), StockoutIng=`KPI-STOCKOUT-ING` (2%, Dashboard=D02). **Never invent IDs like `KPI-D02-OTIF`** — always query the table first. See `references/kpiconfig-table.md` for full dump.
5. **`_ytd` Guard Clause**: All `_Period` measures MUST gate the YTD calculation on `_ctx_year = _cur_year`: `VAR _ytd = IF(_ctx_year = _cur_year, CALCULATE([_Base]))`. Without this guard, YTD returns values for prior years when context year doesn't match current data, causing incorrect period comparisons.
6. **Inverted Logic for Stockout**: Confirm `_StockoutFG` and `_StockoutIng` Delta Label/Chip measures use `_d <= 0` (not `>= 0`) for the positive (green) state.

See `references/d02-slicer-data-sources.md` for confirmed slicer data sources (scm.CustomerSales, scm.CountryZonesMapping).
\t\t\tdisplayFolder: D02\_F   ← 3 tabs (CRITICAL)

\t\tmeasure '_Val' = [_Name]  ← 2 tabs + DAX at 3 tabs
\t\t\tdisplayFolder: D02\_F   ← 3 tabs
```

**Anti-patterns that break displayFolder:**
- `^\t\t\tdisplayFolder` (2 tabs) — measure created, folder NOT applied
- `^\t\t    displayFolder` (2 tabs + 4 spaces) — parse error or ignored
- `^\t\t\t\tdisplayFolder` (4 tabs) — parse error

**Verification:** `head -8 file.tmdl | cat -et` — displayFolder lines MUST show exactly `^I^I^I` (3 tabs).

**Claude Code subagent warning:** Subagents frequently replace tabs with spaces. Always verify and fix indentation after any subagent TMDL work.

## TMDL Reconstruction & Validation Checklist

When regenerating a combined TMDL file (e.g., `v_D02_AllKPIs_Measures.tmdl`) from individual clean files, always apply this validation checklist before finalizing:

1. **Parentheses Balance**: Run a quick Python script to ensure open and close parentheses match exactly.
   ```python
   open_parens = content.count('(')
   close_parens = content.count(')')
   assert open_parens == close_parens, f"Unbalanced: {open_parens} open, {close_parens} close"
   ```
2. **Measure Count**: For 6 KPIs with 10 measures each (Base, Value, Target, Period, Period Prior, Delta, Delta Label, Chip Color, Chip BG Color, Line), verify exactly 60 measures are defined with zero duplicates.
   ```python
   import re
   measures = re.findall(r"measure '([^']+)'\\s*=", content)
   assert len(measures) == 60, f"Expected 60 measures, got {len(measures)}"
   assert len(measures) == len(set(measures)), "Duplicate measures detected"
   ```
3. **D07 V4 Period Pattern Applied**: Ensure ALL `_Period` measures use plain `SELECTEDVALUE('Axis Period'[Axis Period Order])` (NO COALESCE), `CALCULATE(MAX(view[date]), ALL(view))` for `_cur_year`, and `FILTER(ALL(view[date]))` for MTD — no DATESYTD, DATEADD, or ISFILTERED. See "Period Measure Pattern (D07 V4 Proven)" section for the canonical template.
4. **KPIID over KPIName**: Verify all `_Target` measures use `KPIConfig[KPIID] = "KPI-XXX"`. **CRITICAL (CORRECTED 2026-06-09):** KPIIDs are **canonical/shared across dashboards** — NOT dashboard-prefixed. The `Dashboard` column (`D`, `D02`, `D05`, `D07`) is a separate dimension. Validate against `pbi.KPIConfig`. Current verified mapping: OTIF=`KPI-OTIF` (95%, Dashboard=D), OnTime=`KPI-ONTIMESHIP` (90%, Dashboard=D), FillRate=`KPI-FILLRATE` (95%, Dashboard=D), ReqPromAdh=`KPI-INBOUND-PO` (90%, Dashboard=D05), StockoutFG=`KPI-STOCKOUT-FG` (2%, Dashboard=D), StockoutIng=`KPI-STOCKOUT-ING` (2%, Dashboard=D02). **Never invent IDs like `KPI-D02-OTIF`** — always query the table first. See `references/kpiconfig-table.md` for full dump.
5. **`_ytd` Guard Clause**: All `_Period` measures MUST gate the YTD calculation on `_ctx_year = _cur_year`: `VAR _ytd = IF(_ctx_year = _cur_year, CALCULATE([_Base]))`. Without this guard, YTD returns values for prior years when context year doesn't match current data, causing incorrect period comparisons.
6. **Inverted Logic for Stockout**: Confirm `_StockoutFG` and `_StockoutIng` Delta Label/Chip measures use `_d <= 0` (not `>= 0`) for the positive (green) state.

See `references/d02-slicer-data-sources.md` for confirmed slicer data sources (scm.CustomerSales, scm.CountryZonesMapping).

### Power Query M Script Methodology (D02 Standard)

**CRITICAL:** Do NOT use custom SQL queries (`Query="SELECT ..."`) in Power Query for D02. Use native schema/item navigation to preserve query folding, metadata, and align with the existing D02 methodology.

**Correct Pattern (Native Navigation):**
```powerquery
let
    Source = Sql.Database("kingsbi-sqlsrv-prod.database.windows.net", "DataWarehousePBI"),
    v_D02_OTIF_Detail = Source{[Schema="pbi", Item="v_D02_OTIF_Detail"]}[Data],
    // Type enforcement
    Typed = Table.TransformColumnTypes(v_D02_OTIF_Detail, {
        {"DocumentNo", type text},
        {"Quantity", type number}
    })
in
    Typed
```

**Anti-pattern (Custom SQL Query — AVOID):**
```powerquery
let
    Source = Sql.Database("server", "db", [Query="SELECT * FROM pbi.v_D02_OTIF_Detail"])
in
    Source
```

### M Import Script Column Alignment

When creating Power Query M import scripts from SQL views, ALWAYS verify column names match the actual view output:

```sql
-- Run this to get actual column names
SELECT COLUMN_NAME, DATA_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA='pbi' AND TABLE_NAME='v_Daily'
ORDER BY ORDINAL_POSITION
```

Common mismatches:
- View outputs `DocumentNo` but M script references `No` (or vice versa)
- View outputs `PostingDate` but M script references `ShipmentDate`
- View outputs `SnapshotDate` but M script references `ShipmentDate`

**Always cross-reference M script column names against actual view columns before importing.**

### Use TMSL (.tmsl) for TMDL View — NOT C# (.cs)

**CORRECTION from v1:** TMSL works perfectly in Tabular Editor 3's TMDL view when formatted correctly. The user's D07 script (`createOrReplace` + `ref table _Measures`) runs without error. C# scripts (.cs) go in Advanced Scripting (F10) with language selector set to "C#".

### TMSL Format Rules (for TMDL view)

**CRITICAL: Strict adherence to `example.tmsl` structure is mandatory.** Any deviation in tab indentation will cause `InvalidLineType` errors or misaligned display folders. 

**Correct pattern (from local `example.tmsl` — confirmed working):**
```
createOrReplace
\tref table _Measures
\t\tmeasure '_MeasureName' =
\t\t\t\tVAR _x = 1
\t\t\t\tRETURN _x
\t\t\tdisplayFolder: Folder\Subfolder

\t\tmeasure '_OtherMeasure' = [_MeasureName]
\t\t\tdisplayFolder: Folder\Subfolder
```

**CRITICAL TMSL rules:**
1. **ZERO comments** — `//` comments cause `InvalidLineType: Other` error. No comments at all.
2. **Multi-line DAX** uses literal newline characters (`\n`) within a single string, NOT triple backticks, when generated via script, OR use the exact tab-indented block structure as shown above.
3. **Single-line DAX** uses `=`: `measure 'Name' = [OtherMeasure]`
4. **`ref table _Measures`** requires the `_Measures` table to already exist.
5. **No `annotation` lines** in TMDL view — omit them (Power BI regenerates defaults).
6. **Indentation MUST use literal tabs (`\t`)**, NOT spaces. 
   - `createOrReplace` → 0 tabs
   - `ref table _Measures` → 1 tab
   - `measure 'Name' =` → 2 tabs
   - DAX body lines → 4 tabs
   - `displayFolder:` → 3 tabs

### Creating the `_Measures` Table

Before running ANY TMSL script, create `_Measures` in Tabular Editor:
1. Right-click model root → **New** → **Calculated Table**
2. DAX: `_Measures = SELECTCOLUMNS({1}, "Dummy", [Value])`
3. Set **Is Hidden** = `True`

### C# Scripts (.cs) — For Advanced Scripting (F10) Only

C# scripts work in **Advanced Scripting** (F10) with language selector set to "C#". Use when you need helper functions or loops.

```csharp
var table = Model.Tables["_Measures"];
Action<string, string, string> Create = (name, dax, folder) => {
    var m = table.AddMeasure(name, dax);
    m.DisplayFolder = folder;
};
Create("_MeasureName", @"
    VAR _x = 1
    RETURN _x
", "D02\\Folder");
Model.SaveChanges();
Output("✅ Complete");
```

### TMSL Format for Power BI Desktop TMDL View (CORRECTED 2026-06-09)

**User Directive:** The project uses a single `createOrReplace` format pasted directly into Power BI Desktop's TMDL view (or Tabular Editor 3's Advanced Scripting). **There is no separate "pure TMDL" format.** The `.tmsl` extension file with `createOrReplace` + `ref table _Measures` is the canonical file that gets deployed.

**Correct pattern (from `example.tmsl` — confirmed working):**
```
createOrReplace
\tref table _Measures
\t\tmeasure '_Name' =
\t\t\t\tDAX_EXPRESSION
\t\t\tdisplayFolder: D02\_Folder
```

**DO NOT** generate `table _Measures { ... }` syntax — this is NOT the format used. The `createOrReplace` block format is what goes into the TMDL tab.

**Deployment order in Tabular Editor 3 / TMDL view:**
1. `_Measures_Table.tmsl` — creates empty `_Measures` table
2. `Axis_Period_Table.tmsl` — creates the field parameter calculated table
3. `D02_All_Measures_Script.tmsl` — all measures via `createOrReplace`
4. `01_D02_Relationships.tmsl` — RegionKey + CustomerNo relationships

### TMSL vs C# Decision (Tabular Editor Fallback Only)

| Situation | Use |
|-----------|-----|
| Power BI Desktop native TMDL project | **Pure .tmdl** format (no JSON, no TMSL) |
| Advanced Scripting (F10), language = C# | **C#** — helper functions available |
| DAX > 3 lines with complex logic | **Pure .tmdl** with multi-line expression string |
| Bulk creation (50+ measures) | Write a generator script that outputs pure `.tmdl` files |

### Error Quick Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidLineType: Other` | `//` comment in TMSL | Remove ALL comments. Zero comments. |
| `InvalidLineType: NamedObjectWithDefaultProperty` | C# code pasted into TMDL view | Use TMSL format OR paste into Advanced Scripting with language=C# |
| `_Measures table cannot be located` | `_Measures` table doesn't exist | Create it first (Calculated Table DAX) |

---

## Power Query M Debugging Patterns — COMMON ERRORS & FIXES

### Error: "The import X matches no exports"
**Cause:** Referencing a step/query that exists inside another query, not as a separate named query.
**Fix:** Inline the logic or create a separate query. Each Power Query can only reference other **named queries** in the Queries pane.

```
❌ SourceHeaderArchive = SalesHeaderArchive,  // OK if "SalesHeaderArchive" is a query
   LatestHeaderVersions = Table.SelectColumns(ArchiveDeduped, ...)  // BROKEN: ArchiveDeduped is a STEP inside another query
```

**Fix:** Inline the deduplication logic or create a separate named query for the deduped header.

### Error: "Token Eof expected"
**Cause:** Syntax issue — missing closing brace `}`, parenthesis `)`, incomplete statement, or missing `in` clause.
**Fix:** Every `let` must end with `in` + final expression. Check all `{ }`, `[ ]`, `( )` pairs.

### Error: "We cannot convert a value of type Table to type List"
**Cause:** `Table.Column(Current, "No")` fails because `Current` is not a table (wrong query name, or query not loaded).
**Fix:** Use exact query name from Queries pane. Run debug query to list all names:
```powerquery
let Source = #sections[Section1], Names = Record.FieldNames(Source), Filtered = List.Select(Names, each not Text.StartsWith(_, "#")) in Filtered
```

### Error: "The column 'CompositeKey' of the table wasn't found"
**Cause:** Created `CompositeKey` on Current table **before** `Table.Combine`. After combining with Archive (which lacks the column), the combined table has no `CompositeKey`.
**Fix:** Create the composite key **AFTER** the union so it exists on all rows:
```powerquery
Combined = Table.Combine({CurrentFiltered, ArchiveWithPeriod})
CombinedWithKey = Table.AddColumn(Combined, "CompositeKey", each [DocumentNo] & "|" & Text.From([LineNo]))
CurrentKeys = Table.Column(Table.SelectRows(CombinedWithKey, each [SourcePeriod] = "Current"), "CompositeKey")
Deduped = Table.SelectRows(CombinedWithKey, each [SourcePeriod] = "Current" or not List.Contains(CurrentKeys, [CompositeKey]))
```

### Error: "The import X matches no exports"
**Cause:** Same as first error — referencing internal step of another query.
**Fix:** Make queries self-contained. Inline shared logic (like header archive deduplication) rather than referencing another query's steps.

---

## Power Query M UNION Deduplication Patterns

### SalesHeader_Union (Simple — Single PK)
```powerquery
let
    Current = Table.SelectRows(Table.AddColumn(SalesHeader, "SourcePeriod", each "Current"), each [No] <> "" and [No] <> null),
    ArchiveRaw = SalesHeaderArchive,
    ArchiveDeduped = Table.Buffer(Table.SelectRows(Table.Sort(ArchiveRaw, {{"DateArchived", Order.Descending}, {"TimeArchived", Order.Descending}}), each [No] = List.First(Table.SelectRows(ArchiveRaw, (r) => r[No] = [No]))[No])),
    Archive = Table.AddColumn(ArchiveDeduped, "SourcePeriod", each "Archive"),
    Combined = Table.Combine({Current, Archive}),
    CurrentDocNos = Table.Column(Current, "No"),
    Deduped = Table.SelectRows(Combined, each [SourcePeriod] = "Current" or not List.Contains(CurrentDocNos, [No]))
in
    Deduped
```

### SalesLine_Union (Composite PK + Self-Contained Header Dedup)
```powerquery
let
    SourceCurrent = SalesLine,
    CurrentWithPeriod = Table.AddColumn(SourceCurrent, "SourcePeriod", each "Current"),
    CurrentFiltered = Table.SelectRows(CurrentWithPeriod, each [DocumentNo] <> "" and [DocumentNo] <> null and [LineNo] <> 0),
    
    // Self-contained header archive dedup
    SourceHeaderArchive = SalesHeaderArchive,
    HeaderArchiveSorted = Table.Sort(SourceHeaderArchive, {{"DateArchived", Order.Descending}, {"TimeArchived", Order.Descending}}),
    HeaderArchiveGrouped = Table.Group(HeaderArchiveSorted, {"No"}, {{"LatestRow", each Table.FirstN(_, 1), type table}}),
    HeaderArchiveDeduped = Table.ExpandTableColumn(HeaderArchiveGrouped, "LatestRow", List.Difference(Table.ColumnNames(SourceHeaderArchive), {"No"})),
    HeaderVersionDates = Table.SelectColumns(HeaderArchiveDeduped, {"No", "DateArchived", "TimeArchived"}),
    
    // Line archive: join to header versions, then dedup
    SourceLineArchive = SalesLineArchive,
    ArchiveWithHeader = Table.NestedJoin(SourceLineArchive, {"DocumentNo"}, HeaderVersionDates, {"No"}, "HeaderVersion", JoinKind.LeftOuter),
    ArchiveExpanded = Table.ExpandTableColumn(ArchiveWithHeader, "HeaderVersion", {"DateArchived", "TimeArchived"}, {"Header_DateArchived", "Header_TimeArchived"}),
    ArchiveSorted = Table.Sort(ArchiveExpanded, {{"Header_DateArchived", Order.Descending}, {"Header_TimeArchived", Order.Descending}, {"LineNo", Order.Ascending}}),
    ArchiveGrouped = Table.Group(ArchiveSorted, {"DocumentNo", "LineNo"}, {{"LatestRow", each Table.FirstN(_, 1), type table}}),
    ArchiveDedupedLines = Table.ExpandTableColumn(ArchiveGrouped, "LatestRow", List.Difference(Table.ColumnNames(ArchiveExpanded), {"DocumentNo", "LineNo"})),
    ArchiveWithPeriod = Table.AddColumn(ArchiveDedupedLines, "SourcePeriod", each "Archive"),
    
    // Union + cross-dedup (composite key)
    CurrentFiltered2 = Table.SelectRows(Table.AddColumn(SourceCurrent, "SourcePeriod", each "Current"), each [DocumentNo] <> "" and [DocumentNo] <> null and [LineNo] <> 0),
    Combined = Table.Combine({CurrentFiltered2, ArchiveWithPeriod}),
    CombinedWithKey = Table.AddColumn(Combined, "CompositeKey", each [DocumentNo] & "|" & Text.From([LineNo])),
    CurrentKeys = Table.Column(Table.SelectRows(CombinedWithKey, each [SourcePeriod] = "Current"), "CompositeKey"),
    Deduped = Table.SelectRows(CombinedWithKey, each [SourcePeriod] = "Current" or not List.Contains(CurrentKeys, [CompositeKey])),
    Cleaned = Table.RemoveColumns(Deduped, {"CompositeKey"})
in
    Cleaned
```

**Key Principles:**
1. **Create composite keys AFTER union** — so they exist on all rows
2. **Self-contained queries** — inline shared logic rather than referencing other queries' steps
3. **Filter empty PKs in Current** — 169 empty `No` in SalesHeader, 1,807 empty `DocumentNo` in SalesLine
4. **Use `Table.Buffer`** for deduped archive tables to prevent re-evaluation
5. **Filter `SourcePeriod = "Current"`** to extract current-only keys for cross-dedup
6. **ALWAYS add `Table.TransformColumnTypes` AFTER `Table.Combine`** — Power Query can infer text types for numeric columns during UNION, causing DAX type mismatch errors like "DAX comparison operations do not support comparing values of type Text with values of type Integer"

### UNION Type Enforcement Pattern (CRITICAL)

After every `Table.Combine`, add explicit type conversion:

```powerquery
// After Table.Combine({Current, Archive}), BEFORE the final "in":
TypedColumn = Table.TransformColumnTypes(Cleaned, {
    {"LineNo", Int64.Type},
    {"Quantity", type number},
    {"QuantityShipped", type number},
    {"DocumentNo", type text},
    {"SourcePeriod", type text}
})
in
    TypedColumn
```

**Why this is needed:** When `Table.Combine` merges Current and Archive tables, Power Query may infer a text type for numeric columns (especially if Archive source has mixed types or nulls). This causes DAX measures comparing `Quantity > 0` to fail with type mismatch errors. The SQL source may be `decimal`, but Power Query's type inference during UNION can override it.

**Columns to always enforce in SalesLine_Union:**
- `LineNo` → `Int64.Type`
- `Quantity` → `type number`
- `QuantityShipped` → `type number`
- `DocumentNo` → `type text`
- `SourcePeriod` → `type text`

**KPI-specific guidance:**
- KPI-1 (OTIF): Use `SalesLine_Union` — archive has actual ship dates ✅
- KPI-2 (On-Time): Use `SalesLine_Union` — archive has actual ship dates ✅
- KPI-3 (Fill Rate): Use `SalesLine_Union` — full history ✅
- KPI-4 (Stockout FG): Use `DailyInventorySnapshot` — filter `ItemCategory = "FG"`
- KPI-5 (Stockout Ing): Use `DailyInventorySnapshot` — filter `ItemCategory = "RAW"`
- KPI-6 (ReqPromAdh): Use `SalesHeader_Union` — but note sparse archive dates (24%/22%). Consider "Current only" fallback or disclaimer for historical periods.

**Date table range:** Extend to `CALENDAR(DATE(2020,7,1), EOMONTH(TODAY(),0))` to cover archive data.

**Relationships (10 total):**
- ACTIVE: SalesLine_Union[DocumentNo] → SalesHeader_Union[No]
- ACTIVE: SalesHeader_Union[PostingDate] → Date[Date]
- ACTIVE: SalesLine_Union[No] → Item[No]
- ACTIVE: SalesHeader_Union[SelltoCustomerNo] → Customer[No]
- ACTIVE: Item[ItemCategoryCode] → ItemCategory[Code]
- ACTIVE: DailyInventorySnapshot[ItemNo] → Item[No]
- INACTIVE: SalesHeader_Union[DocumentDate] → Date[Date]
- INACTIVE: SalesHeader_Union[RequestedDeliveryDate] → Date[Date]
- INACTIVE: SalesHeader_Union[PromisedDeliveryDate] → Date[Date]
- INACTIVE: DailyInventorySnapshot[SnapshotDate] → Date[Date]

**Row counts (verified 2026-06-06):**
- SalesHeaderArchive: 59,873 rows (2020-07-06 to 2026-06-05)
- SalesLineArchive: 388,267 rows
- SalesHeader (current): 315 rows (2023-04-02 to 2026-08-03)
- SalesLine (current): 2,757 rows
- DailyInventorySnapshot: 97,516 rows (2025-01-02 to 2026-06-05)
- KPIConfig: 20 rows (verified 2026-06-09). See `references/kpiconfig-table.md` for full dump.

**InventoryPostingGroup values (bc.Item):**
| Code | Count | Description |
|------|-------|-------------|
| FG | 668 | Finished Goods |
| RAW | 575 | Raw Ingredients |
| WIP | 650 | Work in Progress |
| PKG | 581 | Packaging |
| DIST | 73 | Distribution Items |
| RESALE | 20 | Resale Items |
| CLEAN | 36 | Cleaning Supplies |
| GS | 42 | General Supply |
| OFFICE | 4 | Office Supplies |
| RAW MAT | 25 | Raw Materials (alternate) |
| PKG EXP | 1 | Packaging Export |
| (blank) | 403 | Unclassified |

**DailyInventorySnapshot ItemCategory values (pre-classified):** FG, RAW, PKG, WIP, DIST, CLEAN, GS, OFFICE, RAW MAT, RESALE

**Archive date completeness (for KPI-6 planning):**
```
Archive Header: RequestedDeliveryDate 24%, PromisedDeliveryDate 22%
Archive Line:   RequestedDeliveryDate 28%, PromisedDeliveryDate 27%
```

## References

- `scripts/query_runner.py` — Reusable AAD-authenticated SQL query runner
- `references/tmdl-format-guide.md` — TMDL indentation rules, table name escaping, pyodbc CREATE VIEW pattern, pre-execution audit checklist, KPI date column reference table
- `references/d02-slicer-data-sources.md` — Confirmed slicer data sources: scm.CustomerSales (Channel), scm.CountryZonesMapping (Region), composite key pattern, M script column alignment
- `references/d07-v4-proven-patterns.md` — D07 V4 canonical DAX patterns (InvInteg Accuracy %, Capacity Util), Axis Period field parameter definition, TMSL structure rules. Source of truth for D02 period measure port.
- `references/azure-sql-access.md` — Azure SQL connection details, schema inspection queries
- `references/kpiconfig-table.md` — Authoritative KPIConfig table dump (21 rows, all KPIIDs, targets, goals). Source of truth for _Target measures.
- `references/d02-otif-date-field-analysis.md` — Session-specific findings on OTIF date field issue and archive table solution
- `references/d02-session-learnings.md` — D02 session learnings
- `references/schema-sync-pattern.md` — Daily schema synchronization workflow
- `references/sql-deduplication-patterns.md` — SQL deduplication patterns
- `references/powerquery-m-debugging-patterns.md` — Power Query M debugging patterns
- `references/adp-workcenter-mapping.md` — ADP ↔ BC work center mapping investigation findings
- `references/pipeline-health-monitoring.md` — Cron job template for monitoring Kings Pastry data pipeline health
- `references/item-category-hierarchy.md` — 2-level `bc.ItemCategory` hierarchy enrichment pattern. Enriches SalesLine_Union chain + Stockout chain (via ItemNo→bc.Item→ItemCategory). COALESCE+NULLIF fallback gives every row a parent. Use `ItemParentCategory` for slicers, `ItemCategoryName` for drill-down.
- `references/d02-null-promised-business-rule.md` — NULL PromisedDeliveryDate policy (2026-06-09): for OTIF/On-Time, NULL promise = on-time by default, **In-Full still enforced for OTIF**. ReqPromAdh stays excluded (adherence KPI meaningless when no promise exists). OTIF 36.4%→34.3%, On-Time 97.7%→99.4% after deployment. SQL CASE patterns and impact matrix in the reference.
- `references/d02-value-measure-merged-pattern.md` — Verified merged-SWITCH pattern for `_OTIF Value` + period-aware `'_OTIF Line'` with `_in_window` gating. Session 2026-06-09 source of truth for applying the merge architecture across the other 5 D02 KPIs.

---

## Kings Pastry D04/D07 Labour KPI — Data Readiness Blockers (2026-06-07)

### ADP Work Center Mapping Status

**Mapping table:** `scm.ADPBCWorkCenterMapping` (60 rows) — maps ADP Dept Codes → **friendly names**, NOT BC `WorkCenter.No` codes

**BC Work Center master:** `bc.WorkCenter` (31 rows) — PK = `No` (e.g., `CAKE`, `F_MIX`, `H_BACK_MIX`)

**Match rate:** Only **5 of 22** mapped work centers match exactly:
- ✅ GB_JELLO_BIG, GB_JELLO_SM, PUFF, SUPPORT, T DOUGH C
- ❌ 17 mismatches (e.g., `CAKE LINE` vs `CAKE`, `BATTER MIX_HOBART` vs `H_BACK_MIX`)

### Production Order → Work Center Link: MISSING

`bc.ProductionOrder` has **NO `WorkCenterCode` column** — only `RoutingNo` (e.g., `RT00284`)

**Routing tables absent from DWH:**
- `bc.Routing` — NOT FOUND
- `bc.RoutingLine` — NOT FOUND
- `bc.ProdOrderRoutingLine` — NOT FOUND

### Impact on Labour KPIs

| KPI | Target | Blocked By |
|-----|--------|------------|
| D04 Labour | 72 cs/lh | Mapping mismatch + no routing tables |
| D07 Labour | 22 cs/lh | Same chain |

### Required Client Deliverables Before KPI Build

1. **Fix mapping table** — `scm.ADPBCWorkCenterMapping.BCWorkCentreNo` must use `bc.WorkCenter.No` codes
2. **Provide routing tables** — `bc.Routing` + `bc.RoutingLine` from BC export/SQL DWH
3. **Define ADP "Production-*" group rows** (27-44) — currently all NULL, need allocation logic
4. **Confirm exclusions** — Office/warehouse/indirect ADP depts (rows 23, 25, 26, 39, 46-60)

### Verification Queries (Reusable)

```sql
-- Work center master
SELECT No, Name, WorkCenterGroupCode FROM bc.WorkCenter ORDER BY No;

-- Mapping table with join test
SELECT m.ADPDeptCode, m.BCWorkCentreNo, wc.No as WC_No, wc.Name as WC_Name, wc.WorkCenterGroupCode
FROM scm.ADPBCWorkCenterMapping m
LEFT JOIN bc.WorkCenter wc ON m.BCWorkCentreNo = wc.No
WHERE m.BCWorkCentreNo IS NOT NULL AND m.BCWorkCentreNo <> 'Not defined yet';

-- Production order sample
SELECT No, Status, RoutingNo, LocationCode FROM bc.ProductionOrder;

-- Check for routing tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA='bc' AND TABLE_NAME LIKE '%Routing%';
```