# Kings Pastry — Supply Chain Control Tower

**Project:** Kings Pastry Supply Chain Control Tower (Power BI dashboard suite)
**Client:** Kings Pastry (bakery, Hong Kong / Canada)
**Repo:** `hdsolanop/Kings-pastry` → `~/projects/hdsolanop/Kings-pastry`
**Asana Project:** Control Tower King's Pastry (gid `1213902233228732`)
**Stakeholders:** Dickie Dik (Production Planning), Andrew Wong (Manufacturing), Anson Lam (SCM/Procurement), Patrick Lam (Logistics/Warehouse), Henry Lam (Customer Service), Martin Huang (Finance)

---

## Build Schedule (revised May 21)

Driver: Business Central dependency shifted the start. Builds run Jun 1-10 in parallel pairs (HS + MR each take 1 dashboard per 2 working days). L3 drill-down for each dashboard is due 1 week after the build.

| Pair | Window | HS builds | MR builds | L3 due |
|------|--------|-----------|-----------|--------|
| Template | May 25-29 | L1+L2 + L3 templates | Same | — |
| Pair 1 | Jun 1-2 | D02 — Service & Fulfillment (6 KPIs) | D05 — Procurement & Supplier (4 KPIs) | Tue Jun 9 |
| Pair 2 | Jun 3-4 | D08 — Alerts & Risks (6 KPIs) | D04 — Production & Supply (4 KPIs) | Thu Jun 11 |
| Pair 3 | Jun 5-8 | D03 — Inventory (8 KPIs) | D06 — Cost & Margin Control (4 KPIs) | Mon Jun 15 |
| Pair 4 | Jun 9-10 | D01 — Executive Overview (merge, 4 KPIs) | D07 — Warehouse Operations (6 KPIs) | Wed Jun 17 |

**Post-build trail:** V2 (Jun 19), Additional Domains (Jun 26), KPI Expansion (Jul 3), Performance Tuning (Jul 10), Usability (Jul 17), Remaining Dashboards (Jul 24), Polish (Jul 31), Deployment (Aug 7), Documentation (Aug 14), Training (Aug 21).

---

## Dashboard Suite (8 dashboards, 42 KPIs)

| ID | Dashboard | Owner | KPIs | KPI list |
|----|-----------|-------|------|----------|
| D01 | Executive Overview | HS (merge) | 4 | OTIF, Days On Hand FG, Inbound PO Adherence, SC Cost % |
| D02 | Service & Fulfillment | HS | 6 | OTIF, On-Time Shipment, Fill Rate, Stockout Rate FG, Stockout Rate Ingredients, Req vs Promised Adherence |
| D03 | Inventory & Working Capital | HS | 8 | DOH FG, DOH Ingredients, DOH Packaging, Inventory Accuracy, Aging FG, Aging RAW, Slow Movers, Below Safety Stock |
| D04 | Production & Supply | MR | 4 | Throughput, Schedule Adherence, Material Availability, Labour |
| D05 | Procurement & Supplier Performance | MR | 4 | Inbound PO Adherence, Lead-Time Adherence, PPV, Supplier Spend Exposure |
| D06 | Cost & Margin Control | MR | 4 | SC Cost %, Outbound Freight, Storage Cost, Labour Cost |
| D07 | Warehouse Operations | MR | 6 | Labour, Picking Accuracy, Capacity Utilization, Inv Integrity FG, Inv Integrity Packaging, Inv Integrity Raw Material |
| D08 | Alerts & Risks | HS | 6 | Open Alerts, Aged Alerts, High-Value Risk, Stockout Risk, Service-at-Risk, Cost Leakage Cases |

**Owner split:** HS (Hernan Solano) = 4 dashboards, 24 KPIs. MR (Manuel Robles) = 4 dashboards, 18 KPIs.

---

## D07 — Warehouse Operations (detailed)

### Slicers
- **Channel Mix:** NOT APPLICABLE (warehouse movements have no channel context)
- **Geographic Region:** NOT APPLICABLE (movements are location-based, not customer-based)
- **Product Category:** APPLICABLE — use **Level 1 (Parent_Category)** from ItemCategory-5722, NOT raw Code (confirmed by Shine)
- **Period Selection:** Only functioning slicer (YTD/MTD/MTO via Calculation Group "TI") — ✅ confirmed working

### Data Sources

**BC Tables:**

| BC Table | Entity | Purpose in D07 | Status |
|----------|--------|----------------|--------|
| Bin (7354) | ENT-201 | Capacity utilization (pallet positions per zone/bin) | ✅ In .pbix as `v_D07_CapacityUtil` (3 rows) |
| Item Category (5722) | ENT-116 | Product hierarchy — use Parent_Category for slicer | ✅ Available |
| Item (27) | ENT-101/111 | Item master (UOM, category, description) | ✅ In model |
| Warehouse Entry (7312) | ENT-102 | Pick accuracy proxy (negative adj in pick bins), stock-in/out, historical inventory | ✅ In .pbix as `v_D07_WarehouseMovements` (~1.96M rows) |
| Value Entry (5802) | ENT-110 | Cases sold for labour KPI — **filtered to 2026+** in pipeline | ✅ In .pbix (2026+ only) |
| Sales Shipment Header (110) | ENT-109 | Outbound cases for labour calc | ✅ In model |
| Sales Shipment Line (111) | — | Shipment detail | ✅ In model |
| Purch Rcpt Header (120) | — | Inbound receiving | ✅ Available |
| Purch Rcpt Line (121) | — | Receiving detail | ✅ Available |
| Item Ledger Entry (32) | ENT-110 | Inventory integrity (FG/Packaging/RM) | ✅ In .pbix as `v_D07_InvIntegrity` |

**SharePoint / Manual Files:**

| File | Purpose | Status |
|------|---------|--------|
| `Labor Cost Master ADP.xlsx` | Labour hours by dept → `v_D07_Labour` | 🔴 0 rows — needs ENT-T07 mapping |
| `Sales Forecast V5 20260323.xlsx` | M+1/M+2/M+3 forecast by SKU (sales updates 1st week/month) | ⚠️ Not in pipeline; for D01/D03 DOH |
| `ADP_BC_work_centre_mapping.xlsx` | 31 ADP dept codes → BC Work Centre No. | 🔴 Task for Shine — 12 done, 19 remaining |
| `General_Entry_Filters.xlsx` | Filter table for large BC accounting tables | ✅ Started — Manuel filling in GL accounts |

**SharePoint source:** `https://kingspastry17.sharepoint.com/sites/KingsPastry2/`

**⚠️ `.url` shortcut files are NOT usable as Power BI data sources.** Must use actual `.xlsx` via SharePoint Folder connector, Graph API, or manual download.

### KPI-LABOUR (cs/lh) Data Source Chain
```
ADP Labor File (SharePoint) → ADP Dept Code
  → ENT-T07 Mapping (ADP Dept → BC Work Centre No.) ← BLOCKED on Shine
  → BC Work Centre (Table 99000760)
  → ValueEntry-5802 (filtered: FG category only, 2026+) → Outbound Cases
  → Cases / Labour Hours = cs/lh
```
Pipeline filter: FG items only (via ItemCategory join), 2026+ for size.

### Build Status (as of Jun 2, 2026)
- ✅ PeriodSelection slicer — working
- ✅ Order Picking Accuracy — has data
- ✅ Capacity Utilization — has snapshot data
- ✅ Inventory Integrity FG/Packaging/RM — has data
- ✅ Historical inventory table — built by Manuel (daily grain, stock-in/out by SKU)
- 🔴 Labor — blocked (no data until ENT-T07 mapping + ADP file loaded)

### New Blockers (added Jun 2)

| # | Item | Owner | Priority |
|---|------|-------|----------|
| 6 | **Physical/Manual Count table for Inventory Integrity** — Inv Integrity KPIs = system qty vs physical qty. Need a source for manual count data per Site/Zone/Item to compare against `v_D07_InvIntegrity`. Shine to confirm: (a) does a digital count log exist? (b) if not, build Excel/SharePoint input table. Without this, integrity % = system vs itself, no real variance. | Shine | 🔴 CRITICAL |
| 7 | **Capacity KPI — pallet unit definition in Bin (7354)** — Need Shine to confirm: (a) exact field name for max pallet positions per zone, (b) is 1 pallet = 1 physical position or weight/volume-based? (c) Location Code + Zone Code field names for Site (WH1/3PL) × Zone (Staging/Cooler, Freezer, Ambient) filter, (d) bins to exclude (quarantine, etc.). Target: star model with Sites × Zones × Pallet Capacity × Occupied × Utilization %. | Shine | 🟡 HIGH |

### V2 — Labour KPI: Inbound kg/L → Equivalent FG Cases (BOM Conversion)

> V2 enhancement: convert inbound RM receipts (kg, liters) into estimated equivalent FG cases using the BOM.

**Concept:** Currently Labour KPI = outbound cases / labour hours (cs/lh). Inbound receipts in kg/liters not comparable. Using BOM:
```
Inbound: 500 kg flour → BOM: 2 kg/case → 250 equivalent cases
Total throughput cs/lh = (outbound cases + inbound equiv cases) / labour hours
```

**Data sources:**
- BOM: BC Production BOM Header (99000771) + BOM Line (99000772) — link FG Item No. → Component Item No. + Quantity Per
- Inbound receipts: Purchase Receipt Line (121) or Item Ledger Entry (positive/purchase), filtered to RM/Ingredient category
- UOM alignment: Item (27) Base Unit of Measure

**5 questions for Shine:**
1. BOM Header 99000771 field names (No., FG Item No., Status, Version)
2. BOM Line 99000772 field names (Item No., Quantity Per, UOM)
3. BOM versioning — how to select "current active" version per FG?
4. Ingredient category codes (same as D02 open item #15)
5. Multiple FG per ingredient — weighted split or primary FG assignment?

**Notes:** Additive to base Labour KPI — outbound cs/lh stays primary. Manuel builds once BOM table access confirmed. Priority: V2 (after base Labour + ENT-T07 mapping resolved).

### Retrospective Historical Inventory
- New feature: daily historical stock levels per SKU going back to earliest Warehouse Entry
- SQL script: `Sprint 4 - template development/D07_Historical_Inventory_Retrospective.sql`
- Logic: Start from current Item Ledger balance, walk backwards through Warehouse Entry
- Output: `pbi.v_D07_HistoricalInventory` — SKU, Product_Name, Date (DD/MM/YYYY), Quantity, UOM, Item_Category, Stock_In, Stock_Out

### Design Reference
- Full build guide: `Sprint 4 - template development/d07-handoff.md`
- 6 KPI cards in 2×3 grid
- Page background: `#FFF8F1`, Card backgrounds: white
- Brand colors: Royal Purple `#6F2365`, Rich Purple `#3F0938`, Egg Yellow `#FDB831`
- Only PeriodSelection slicer (YTD/MTD/MTO)
- Snapshot KPIs (Capacity, InvIntegrity) show `--` for delta chip
- Calculation Group "TI" with 4 items: Current, Latest Month, Prior Year, Sparkline

---

## Archive Tables for Historical Order Data — CRITICAL (added Jun 2)

**Finding:** Sales Order tables (36/37) only contain active/open orders. Historical closed orders from 2020+ are in archive tables.

| Archive Table | Table # | OData Endpoint (TBC) | Purpose |
|---------------|---------|---------------------|---------|
| SalesHeaderArchive | 5107 | `SalesHeaderArchive` *(confirm)* | Historical closed sales order headers |
| SalesLineArchive | 5108 | `SalesLineArchive` *(confirm)* | Historical closed sales order lines |

**Without archive tables, all historical KPIs only see active orders** — affects OTIF, On-Time Shipment, Fill Rate, Stockout FG/Ing, Req/Promised for D02; Stockout calculations for D03; Inbound PO Adherence for D05.

**Shine to confirm:**
1. Are SalesHeaderArchive (5107) and SalesLineArchive (5108) available as OData endpoints?
2. What are the exact endpoint names in BC sandbox?
3. Does the same archive pattern exist for Purchase Orders? (PurchaseHeaderArchive + PurchaseLineArchive)
4. Does the same exist for Production Orders? (ProdOrderArchive)

**Status:** 🔴 CRITICAL — blocks all historical KPI calculations across D02, D03, D04, D05.

---

## D08 — Exception & Risk Cockpit — DEFERRED TO V2

- **Reason:** Depends on all 7 operational dashboards being live first
- **Estimated start:** Jul 2026 (after all L3 complete)
- **Alert delivery method:** Daily digest
- **Dependencies:** ENT-T06 threshold table, all operational dashboards live
- **Tracker:** `V2_Out_of_Scope_Tracker.md`

---

## D02 — Service & Fulfillment (key findings from Client_Data_Questions.docx + API data)

### New Information / Confirmations
1. **Fill Rate UOM:** FG level is all by cases. No mixed-UOM conversion needed — simplifies calculation.
2. **Stockout-FG:** No separate backorder file (ENT-207). Use BC Sales Orders (archive, max version). Outstanding qty = Quantity – Quantity Shipped.
3. **Stockout-ING:** No separate inbound receiving schedule (ENT-209). Use BC Purchase Lines (Table 39) with Promised_Receipt_Date, Qty=0 filter.
4. **Req vs Promised Adherence:** Promised_Delivery_Date is actively maintained by CS team (confirmed with Henry).
5. **Channel slicer:** ENT-217 (SharePoint) has Channel column. Need to confirm exact column header name and code match with BC dimension values.
6. **Region slicer:** ENT-217 has Customer No. but no State/Province. Join: ENT-217 → BC Customer → Ship-to Address (Table 222) → County. Feasible but needs region value cleanup. Use Posted Sales Invoice table for correct ship-to address.
7. **Product Category:** Item codes in ENT-217 match BC Item No. exactly — no cross-reference mapping needed.
8. **Inventory Posting Group Codes (CONFIRMED from API extraction, Jun 4):** FG = Finished Goods, RAW = Raw Ingredients, PKG = Packaging Items, WIP = Work in Progress, DIST = Distribution Items, GS = General Supply. **This UNBLOCKS KPI-4 (Stockout FG) and KPI-5 (Stockout Ingredients).** Filter: `bc_Item[Inventory_Posting_Group] = "FG"` or `"RAW"`.
9. **API vs SQL field names:** BC API uses camelCase (number, displayName, itemCategoryCode, inventoryPostingGroupCode, shipmentDate, postingDate). SQL DDBB uses PascalCase (No, Description, Item_Category_Code, Inventory_Posting_Group, Shipment_Date, Posting_Date). Power BI uses whichever source you connect to.
10. **OTIF join path:** Start with header-level promise (SalesShipmentLine → SalesShipmentHeader → SalesHeader). Switch to line-level (SalesLineArchive) if data looks wrong. Key question: Is Promised_Delivery_Date at header or line level in the SQL DDBB?
11. **bc.SalesShipmentLine has Shipment_Date at line level** — this is the actual delivery date for OTIF "on-time" check. Confirmed from API data (48,637 rows).
12. **bc.ItemCategory has NO parent_category field in API** — the 77 category codes ARE the Level 1 values. The SQL DDBB may have Parent_Category.

### D02 Build Knowledge (Jun 4)
- D02-specific build knowledge base at: `D02_Service_Fulfillment/` folder in Kings Pastry repo
- Contains: Build plan, data source map, data structure analysis, DAX measures, KPI definitions, validation checklist
- Subfolder structure: Build/, Data_Sources/, DAX/, Documentation/, Validation/
- Key open questions: Promised_Delivery_Date location, pbi.DailyInventorySnapshot column names, Order_No join format
- OTIF-first approach: Build OTIF card first (most complex join), validate data model, then duplicate for remaining 5 KPIs

---

## D05 — Procurement & Supplier Performance (key findings from Client_Data_Questions.docx)

### New Information / Confirmations
1. **Inbound PO + Lead Time:** Promised_Receipt_Date actively maintained (confirmed).
2. **Lead_Time_Calculation:** At **Item Card** level, NOT Vendor level — data source change from original assumption.
3. **"In-Full" tolerance:** Receiving qty ≥ ordered qty AND ≤ +5% of ordered qty = in full. Less than ordered = not complete.
4. **PPV:** No material price budget file (ENT-204). PPV = PO price vs invoice price only, not budget variance. Scope reduction.
5. **Channel/Region slicers:** NOT APPLICABLE. Confirmed acceptable.

---

## L1 Global Configuration (client-confirmed values)

### Revenue GL Accounts
- Gross Sales: **31110** (Sales - General)
- Deductions: 31950, 31952, 41186, 41187, 41188, 44220, 44221, 44222, 44223, 44224
- Net Revenue = Gross Sales minus all deductions

### Cost GL Accounts (see also `data_source/General_Entry_Filters_COMPLETE.md`)
- Freight without PO: **42172, 42170**
- Freight with PO: posted purchase invoice lines (charge item type) — NOT a separate GL account
- Storage (3rd party): **42375**
- Labour cost GL accounts: **STILL UNKNOWN** — need confirmation from Finance (Martin Huang)

### OTIF / On-Time Definition (Andrew Wong)
- **On-time = Actual ship date (posting date) equals Planned ship date (promised delivery date)**
- Both Requested_Delivery_Date and Promised_Delivery_Date are actively used by KP sales team

### Inventory
- Costing method: **FIFO** (confirmed)
- Safety_Stock_Quantity: populated (filter items with safety stock quantity > 0)
- BOM (ENT-107): complete — group by BOM version, use max active version

### Work Centre Mapping (ENT-T07) — CRITICAL
ADP → BC Work Centre mapping table needs 31 codes mapped. 12 provided in client doc, 19 remaining. Partial mapping:

| ADP Code | ADP Description | BC Work Centre |
|----------|---------------|----------------|
| BMIX00 | Back Mixing | BATTER MIX_HOBART, BTTER MIX_ITALY |
| CKL-00 | Cake Line | CAKE LINE, CREAM KETTLE |
| FMIX00 | Front Mixing | CREAM MIX_HOBART, CREAM MIX_ITALY_MIXER |
| GBL-00 | Golden Blends Line | GB_JELLO_BIG, GB_JELLO_SM, GB_PWDR |
| JRL-00 | Jelly Roll Line | JELLY ROLL LINE |
| PFL-00 | Puff Line | FRONT MIX, PASTRY DOUGH MIX, PASTRY LAMINATION, PUFF, PUFF ASSEMBLING |
| PRM-00 | Premium Line | *(not mapped yet)* |
| TSL-00 | Egg Tart Line | T DOUGH C, TART CUTTER, TART SHEETER, TART FORMER_L, TART FORMER_S, TRAY FORMER |
| NSG-00 | Night Shift (General) | Not defined yet |
| SUL-00 | Supporting / Indirect Labour | SUPPORT |
| WHG-00 | Warehouse General | Not defined yet (all warehouse labor currently under Plant) |
| CLG-00 | Cleaning / Sanitation | Not defined yet |

---

## Slicer Applicability Matrix (all dashboards) — FINAL

| Slicer | D01 | D02 | D03 | D04 | D05 | D06 | D07 | D08 |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|
| Channel | Partial* | Yes | No | No | No | Partial* | No | Partial |
| Region | Yes | Partial** | No | No | No | No | No | Partial |
| Product Category | Yes | Yes | Yes | Yes | Yes | No | Yes*** | Mostly |
| Period | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |

*D01/D06: Client confirmed Channel is on Customer Card, NOT on Sales Order Line or GL entries. Channel slicer effectively only works on D02 (via ENT-217 file). Scope reduced.

**D02 Region: Indirect join via Customer → Ship-to Address. Needs cleanup. Use Posted Sales Invoice table for correct ship-to address.

***Product Category: Use Level 1 (Parent_Category) from ItemCategory-5722, NOT raw Code. Confirmed by Shine.

---

## KPI Thresholds (proposed, pending client confirmation)

| KPI | Target | Alert Threshold |
|-----|--------|-----------------|
| OTIF % | >= 95% | < 90% = RED |
| On-Time Shipment % | >= 95% | < 90% = RED |
| Fill Rate % | >= 98% | < 95% = RED |
| DOH FG | 14-45 days | < 7d or > 60d |
| DOH Ingredients | 10-30 days | < 5d = RED |
| DOH Packaging | 10-30 days | < 5d = RED |
| Inventory Accuracy % | >= 99% | < 97% = RED |
| Stockout Rate FG % | < 2% | > 5% = RED |
| Inbound PO Adherence % | >= 90% | < 80% = RED |
| Lead-Time Adherence % | >= 85% | < 75% = RED |
| PPV | +/- 5% vs budget | > +/- 10% = RED |
| Throughput | > 90% of target | < 80% = RED |
| Schedule Adherence % | >= 90% | < 80% = RED |
| Cases per Labour Hr | TBD with Ops | < 80% of target = RED |
| SC Cost % of Revenue | <= 12% | > 15% = RED |
| Outbound Freight Cost | Delivery cost % net sales > 4.5% = RED | — |
| Storage Cost | Storage cost % net sales > 1.9% = RED | — |
| Capacity Utilization % | 60-85% | > 90% or < 40% |
| Picking Accuracy % | >= 99.5% | < 98% = RED |

**D08 Alert delivery:** Daily digest

---

## Data Source Register (key entities)

| Entity | Source | Table/File | Status |
|--------|--------|------------|--------|
| ENT-101 | BC | Item Ledger Entry (32) | ✅ In .pbix |
| ENT-102 | BC | Warehouse Entry (7312) | ✅ In .pbix |
| ENT-103 | BC | Purchase Header/Line (38/39) | ✅ Available |
| ENT-104 | BC | Purchase Receipt (120/121) | ✅ Available |
| ENT-105 | BC | Production Order (5405) | ✅ Available |
| ENT-107 | BC | BOM Header/Line (99000760/71) | ✅ Complete |
| ENT-108 | BC | Sales Header/Line (36/37) | ✅ Available |
| ENT-109 | BC | Sales Shipment (110/111) | ✅ In model |
| ENT-110 | BC | Value Entries | ✅ In model |
| ENT-111 | BC | Item (27) | ✅ In model |
| ENT-112 | BC | Vendor (23) | ✅ Available |
| ENT-113 | BC | Customer (18) | ✅ Available |
| ENT-118 | BC | Ship-to Address (222) | ✅ Available |
| ENT-201 | BC | Bin (7354) | ✅ In .pbix |
| ENT-215 | SharePoint | Sales Forecast file | ⚠️ Received by email, not yet in pipeline |
| ENT-401 | SharePoint | ADP Labor Cost Master | ⚠️ File exists, not yet loaded |
| ENT-T04 | BC | Dimension Value (349) — Channel | ⚠️ Confirm dimension code name |
| ENT-T05 | BC | GL Account (15) → Cost Bucket mapping | ⚠️ Finance mapping session needed |
| ENT-T06 | PBI | 13_Targets sheet | ⏳ Pending client threshold confirmation |
| ENT-T07 | Manual | ADP Dept → BC Work Centre mapping | 🔴 CRITICAL — 19 codes remaining |
| ENT-T08 | Manual | State/Province → Region mapping | 🟡 Groupings confirmed, build table |

---

## Open Questions (as of Jun 2, 2026 — v2 after full D01-D08 analysis)

### 🔴 CRITICAL (block build)

| # | Question | Who | Dashboards |
|---|----------|-----|-----------|
| 1 | Complete 19 remaining ADP→BC Work Centre mappings | Shine | D04, D07 |
| 2 | G/L Account (15) endpoint never configured — configure export | Shine | D01, D06 |
| 3 | Physical/Manual Count table for Inventory Integrity — D03 + D07. Does a digital count log exist? If not, build SharePoint/Excel input table. | Shine | D03, D07 |
| 4 | ENT-117 Posted Purchase Invoice endpoint — verify configured in BC export | Shine | D05 |

### 🟡 HIGH

| # | Question | Who | Dashboards |
|---|----------|-----|-----------|
| 5 | Which GL accounts do labour costs post to in BC? | Finance (Martin Huang) | D04, D06 |
| 6 | Confirm ENT-217 Channel column header name + code values | Manuel/Shine | D02 |
| 7 | Promised_Receipt_Date completeness on ENT-103 — actively maintained for recent POs? | Shine | D05 |
| 8 | Lead_Time_Calculation source — PO header (ENT-103) vs Vendor (ENT-112)? | Shine | D05 |
| 9 | BOM version selection logic — how to pick "current active" version per FG? | Shine | D03, D04 |
| 10 | Production Order status mapping — which statuses = "Finished"? | Shine | D04 |
| 11 | D07 Capacity KPI — Bin (7354) field names for max positions, UOM, Location/Zone codes | Shine | D07 |
| 12 | Sales Forecast file (ENT-215) — SharePoint location + format confirmation | Client/Shine | D01, D03 |
| 13 | GL Account → Cost Bucket mapping (ENT-T05) — confirm SC Labour + Other accounts | Finance + Shine | D01, D06 |

### 🟢 MEDIUM / LOW

| # | Question | Who | Dashboards |
|---|----------|-----|-----------|
| 14 | Freight-with-PO capture — validate ENT-117 charge item approach | Manuel | D01, D06 |
| 15 | Pick accuracy proxy — do negative WH adjustments correlate with actual errors? | Manuel | D07 |
| 16 | D07 V2: BOM table access for inbound kg→cases conversion | Shine | D07 |
| 17 | Item UOM alignment — Purchase Receipt vs PPV price (kg vs lbs vs cases) | Shine | D05, D06 |
| 18 | Packaging category code confirmation | Shine | D02, D03 |

---

## Data Source Documentation (all dashboards — v2 Jun 2)

Per-dashboard data source docs now exist for all 8 dashboards:
- Synthesis docs: `D0X_Data_Source_Synthesis.md`
- Per-KPI docs: `D0X_KPI[N]_[Name]_Data_Sources.md`
- Connection lists: `D0X_Data_Source_Connection_List.md`

Full index at `references/kings-pastry-data-source-docs.md`.

---

## Key File Locations

| File | Path |
|------|------|
| V2/out-of-scope tracker | `V2_Out_of_Scope_Tracker.md` |
| D07 data source reference | `D07_Data_Source_Reference.md` |
| GL account filters (complete) | `data_source/General_Entry_Filters_COMPLETE.md` |
| Historical inventory SQL | `Sprint 4 - template development/D07_Historical_Inventory_Retrospective.sql` |
| D07 build guide | `Sprint 4 - template development/d07-handoff.md` |
| KPI spec | `KPI_Data_Spec_Template_V6.xlsx` |
| Design system | `design_guide.html` |
| Build org chart | `Dashboard_OrgChart.html` |
| Prototype | `https://scm-analytics.com/Solutions/KingsPastry/` |
| Client requirements | `Client_Data_Questions.docx` (V2.0, May 2026) |
Current prototype + documentation: `https://scm-analytics.com/Solutions/KingsPastry/`
Client requirements doc: `Client_Data_Questions.docx` (V2.0, May 2026)
KPI spec: `KPI_Data_Spec_Template_V6.xlsx` (18 sheets, 42 KPI blocks across 8 dashboards)
Design system: `design_guide.html` (token-driven, maps to Power BI themes)
Build org chart: `Dashboard_OrgChart.html` (hierarchy + schedule)
