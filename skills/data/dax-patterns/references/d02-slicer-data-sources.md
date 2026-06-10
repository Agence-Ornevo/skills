# D02 Slicer Data Sources — Confirmed 2026-06-09

## Channel Mix Slicer

**Source table:** `scm.CustomerSales` (NOT `bc.Customer.GlobalDimension1Code`)

**Channels (8):** CLUB, CONEXUS, ENSON, FS DIRECT, FS DISTRIBUTOR, HF FOODS, RETAIL DIRECT, RETAIL DISTRIBUTOR

**Join:** `v_D02_SalesHeader_Union[SelltoCustomerNo]` → `scm_CustomerSales[CustomerNo]`

**Relationship:** Active, single direction

**Scope:** Only D02 (sales) dashboards. D03/D04/D05/D07 won't support channel slicer (acceptable per docx).

## Geographic Region Slicer

**Source table:** `scm.CountryZonesMapping` (64 rows, Country+Region+State)

**Regions:** US East, US West, US Central, Canada East, Canada West

**Join:** Composite key — SalesHeader[ShiptoCountryRegionCode] + [ShiptoCounty] → CountryZonesMapping[Country] + [State]

**Implementation:** Create RegionKey in both tables (Country pipe State), join on RegionKey.

## Item Category Slicer (ADDED 2026-06-09)

**Source:** `bc.ItemCategory` via join chain (see `references/item-category-hierarchy.md`)

All daily views now expose `ItemCategoryName` (friendly leaf) and `ItemParentCategory` (top-level group). Use **`ItemParentCategory`** as the slicer column — it gives clean top-level groups (BITE, TART, BAR CAKES, MINI CAKES, etc.). Use `ItemCategoryName` for drill-down detail tables.

**Top 5 parent categories by volume:** BITE (62K lines), TART (27K), BAR CAKES (22K), CELINE (16K), MINI CAKES (15K).

**Scope:** Available on OTIF_Daily, OnTime_Daily, FillRate_Daily, OTIF_Detail, Stockout_Daily. NOT on ReqPromAdh_Daily (header-level, no item context).

## Level 3 Table View

**New view needed:** `pbi.v_D02_OTIF_Detail` at order-line grain with boolean flags (IsOnTime, IsInFull, IsOTIF as "Yes"/"No"), RegionKey, SelltoCustomerNo.

## Level 3 Multi-Series Chart

**Series:** OTIF by year (all years), On-Time (last year only), Fill Rate (last year only), OTIF Target (constant line)

**X-axis:** Date[Date] — all series must align to same x-values (Jan 1st = one point per series)

**New measures needed:**
- `_OnTime Line Last Year` — filtered to last year via USERELATIONSHIP
- `_FillRate Line Last Year` — filtered to last year via USERELATIONSHIP
- `_OTIF Variance` = [_OTIF Period] - [_OTIF Target]

## Level 1 Period Fix

**Issue:** Period slicer doesn't change x-axis accordingly.

**Root cause:** `_Period` measure uses `ALL( view[Date] )` which removes all date filters, but x-axis is bound to `Date[Date]` via active relationship. Not synchronized.

**Fix approach:** Filter `Date[Date]` table directly instead of view date column, or use DATESBETWEEN.