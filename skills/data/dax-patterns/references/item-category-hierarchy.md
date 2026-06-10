# Item Category Hierarchy — Kings Pastry Enrichment Pattern

**Table:** `bc.ItemCategory`
**Verified:** 2026-06-09 (77 rows: 51 children + 26 top-level parents)

## Hierarchy Structure

| Column | Type | Meaning |
|--------|------|---------|
| `Code` | nvarchar | Primary key — category code (e.g., `BAR CAKE 12 X 4`, `BAR CAKES`) |
| `ParentCategory` | nvarchar | Parent group code; NULL for top-level categories |
| `Description` | nvarchar | Human-readable leaf name (e.g., "Bar Cake 12 X 4") |
| `Indentation` | int | BC hierarchy depth (0/NULL or 1) |
| `HasChildren` | bit | True for parent categories |

**Two-level hierarchy only.** No deeper nesting. When `ParentCategory IS NULL`, the row is itself a top-level group (e.g., `BAR CAKES`, `TART`, `FG`, `RAW`).

## Enrichment Pattern (CRITICAL)

Add two columns to any view that needs category grouping:

| Output Column | Expression |
|---------------|------------|
| `ItemCategoryName` | `ic.Description` (friendly leaf name) |
| `ItemParentCategory` | `COALESCE(NULLIF(ic.ParentCategory, ''), ic.Code)` |

**The COALESCE+NULLIF logic ensures every row always has a meaningful parent value.** When a category has no parent (e.g., `TART`, `RAW`, `FG`), it falls back to its own code — top-level group = itself.

## Join Chain A: Sales views (ItemCategoryCode on line)

```sql
-- Join from SalesLine_Union which already has ItemCategoryCode
LEFT JOIN bc.ItemCategory ic
    ON al.ItemCategoryCode = ic.Code
```

Used in: `v_D02_SalesLine_Union`, propagated to `v_D02_OTIF_Daily`, `v_D02_OnTime_Daily`, `v_D02_FillRate_Daily`, `v_D02_OTIF_Detail`.

## Join Chain B: Inventory/stockout views (ItemNo → Item → ItemCategory)

```sql
-- Chain through bc.Item to get ItemCategoryCode, then ItemCategory
FROM pbi.DailyInventorySnapshot dis
LEFT JOIN bc.Item i
    ON dis.ItemNo = i.No
LEFT JOIN bc.ItemCategory ic
    ON i.itemCategoryCode = ic.Code
```

Used in: `v_D02_Stockout_Daily`. ItemNo is the join key that enriches the snapshot even though it has no `ItemCategoryCode`.

## Deployment Stats (2026-06-09)

| View | Total rows | % enriched |
|------|------------|-----------|
| `v_D02_SalesLine_Union` | 192,237 | 99.8% |
| `v_D02_Stockout_Daily` | 97,671 | 99.9% / 100% (parent) |

## Top 10 Parent Categories (by sales line volume)

| Parent | Lines |
|--------|-------|
| BITE | 62,189 |
| TART | 27,264 |
| BAR CAKES | 21,667 |
| CELINE | 15,550 |
| MINI CAKES | 15,147 |
| SEMI | 12,873 |
| DIMSUM | 6,978 |
| MINI PASTRY | 6,441 |
| MINI BAKERY | 5,067 |
| ROUND CAKES | 4,499 |

## Power BI Slicer Pattern

Use `ItemParentCategory` as the slicer column for category filtering — it gives clean top-level group values. Use `ItemCategoryName` for drill-down / detail tables.

**Relationships (PBI model):**
- `v_D02_SalesLine_Union[ItemCategoryCode]` → `bc.ItemCategory[Code]` (active)
- `bc.ItemCategory[ParentCategory]` → `bc.ItemCategory[Code]` (self-join, inactive — only activate via USERELATIONSHIP or Power Query merge)

## Power Query M Script Column List

When importing enriched views, add these two column type enforcements:

```powerquery
{"ItemCategoryName", type text},
{"ItemParentCategory", type text},
```

## SQL View Template Fragment

```sql
-- In the SELECT clause (after existing columns):
ic.Description AS ItemCategoryName,
COALESCE(NULLIF(ic.ParentCategory, ''), ic.Code) AS ItemParentCategory,

-- In the FROM clause:
LEFT JOIN bc.ItemCategory ic
    ON al.ItemCategoryCode = ic.Code
```

## When to Apply

Apply to any D02 view that:
1. Has an `ItemCategoryCode` column OR
2. Has an `ItemNo` column that can join to `bc.Item.No` → `bc.Item.itemCategoryCode`

**Skip** views that only have header-level data (e.g., `v_D02_ReqPromAdh_Daily` which is header grain, no item context).
