# D02 — Service & Fulfillment: Build Knowledge Base

> **Source:** Wireframe V9 + KPI spec V6 + D02 Documentation.md + BC API extraction data
> **Last updated:** 2026-06-04

---

## KPI Definitions (from wireframe V9)

| # | KPI | Target | Unit | Goal | Definition |
|---|-----|--------|------|------|------------|
| 1 | OTIF | 95 | % | Higher | Orders delivered on time and in full, with on-time anchored to customer request and promise alignment. |
| 2 | On-Time Shipment | 95 | % | Higher | Orders where the promised date matched the requested date and shipment met that promise. |
| 3 | Fill Rate | 98 | % | Higher | Percentage of ordered cases fulfilled. |
| 4 | Stockout Rate FG | 5 | % | Lower | Frequency of finished goods zero-availability situations. |
| 5 | Stockout Rate Ingredients | 5 | % | Lower | Frequency of ingredient zero-availability situations. |
| 6 | Requested vs Promised Adherence | 95 | % | Higher | Orders where promised date meets request. |

**Removed KPIs:** Delivery Delay Rate, Order Cycle Time

---

## Data Sources (confirmed from API extraction)

### Fact Tables

| Table | BC Object | ENT ID | Rows | Key Fields |
|-------|-----------|--------|------|------------|
| bc.SalesShipmentHeader | 110 | ENT-109 | 6,218 | No, Order_No, Posting_Date (= actual ship date), Sell_to_Customer_No |
| bc.SalesShipmentLine | 111 | ENT-109 | 48,637 | Document_No, No (Item), Quantity, Shipment_Date |
| bc.SalesHeader | 36 | ENT-108 | unknown | No, Requested_Delivery_Date, Promised_Delivery_Date, Document_Date, Status |
| bc.SalesHeaderArchive | 5107 | ENT-108 | 3,366 | Same + Date_Archived, Version_No |
| bc.SalesLineArchive | 5108 | ENT-108 | 20,558 | Document_No, No (Item), Quantity, Requested_Delivery_Date, Promised_Delivery_Date, Shipment_Date, Quantity_Shipped |
| bc.ItemLedgerEntry | 32 | ENT-110 | 224,603 | Entry_No, Item_No, Posting_Date, Entry_Type, Quantity |

### Dimension Tables

| Table | BC Object | ENT ID | Rows | Key Fields |
|-------|-----------|--------|------|------------|
| bc.Item | 27 | ENT-111 | 3,023 | No, Description, Item_Category_Code, Inventory_Posting_Group |
| bc.ItemCategory | 5722 | ENT-116 | 77 | Code, Description (Level 1 = the code itself) |
| bc.Customer | 18 | ENT-113 | unknown | No, Name, Country_Region_Code |

### Pre-built Views (pbi schema)

| Table | Purpose | Column Verification Needed |
|-------|---------|---------------------------|
| pbi.DailyInventorySnapshot | Daily stock snapshot | Snapshot_Date, Item_No, Location_Code, Available_Qty |
| pbi.KPIConfig | KPI targets | KPIName, Target |
| pbi.DeptMapping | Department mapping | — |

---

## Critical Data Findings

### Inventory Posting Group Codes (CONFIRMED from API data)
```
FG     = Finished Goods      -> KPI-4 Stockout Rate FG filter
RAW    = Raw Ingredients     -> KPI-5 Stockout Rate Ingredients filter
PKG    = Packaging Items
WIP    = Work in Progress
DIST   = Distribution Items
GS     = General Supply
OFFICE = Office Supplies
CLEAN  = Cleaning Supplies
```
**This UNBLOCKS KPI-4 and KPI-5.** Filter: `bc_Item[Inventory_Posting_Group] = "FG"` or `"RAW"`.

### Item Ledger Entry Types
```
Output, Sale, Purchase, Consumption, Transfer, Positive Adjmt., Negative Adjmt.
```

### Item Category Codes (77 total -- these ARE Level 1)
RAW, FG, PKG, WIP, DIST, GS, 1/2 SLAB, 1/4 SLAB, BAR CAKES, CAKES ROLLS, DIMSUM, MOONCAKES, MINI CAKES, MINI PASTRY, ROUND CAKES, etc.

### API vs SQL Field Name Mapping (key fields)
| API (camelCase) | SQL (PascalCase) |
|-----------------|------------------|
| number | No |
| displayName | Description |
| itemCategoryCode | Item_Category_Code |
| inventoryPostingGroupCode | Inventory_Posting_Group |
| baseUnitOfMeasureCode | Base_Unit_of_Measure |
| documentNo | Document_No |
| lineObjectNumber | No (Item) |
| quantity | Quantity |
| shipmentDate | Shipment_Date |
| postingDate | Posting_Date |
| orderNumber | Order_No |
| customerNumber | Sell_to_Customer_No |
| sellToCountry | Country_Region_Code |
| itemNumber | Item_No |
| entryType | Entry_Type |

---

## OTIF Join Path

**Option A (header-level promise -- RECOMMENDED for initial build):**
```
SalesShipmentLine -> SalesShipmentHeader (Document_No = No)
                  -> SalesHeader (Order_No = No) <- Promised_Delivery_Date + Requested_Delivery_Date
                  -> Item (lineObjectNumber = No)
                  -> Customer (Sell_to_Customer_No = No)
```

**Option B (line-level promise -- more accurate):**
```
SalesShipmentLine -> SalesShipmentHeader (Document_No = No)
                  -> SalesLineArchive (Document_No + No match) <- Promised_Delivery_Date at line level
                  -> Item (lineObjectNumber = No)
                  -> Customer (Sell_to_Customer_No = No)
```

**On-Time check:** SalesShipmentLine[Shipment_Date] <= SalesHeader[Promised_Delivery_Date]
**In-Full check:** SalesShipmentLine[Quantity] >= SalesLineArchive[Quantity]
**Date table link:** SalesShipmentHeader[Posting_Date] -> Date[Date] (ACTIVE)

**Open question:** Is Promised_Delivery_Date at header or line level in the SQL DDBB? Start with header (Option A). Switch to line (Option B) if data looks wrong.

---

## Open Questions for D02 Build

| # | Question | Impact | How to Resolve |
|---|----------|--------|----------------|
| 1 | Promised_Delivery_Date location (header vs line)? | OTIF formula | Check D07 PBIX or run SQL query |
| 2 | pbi.DailyInventorySnapshot column names? | KPI-4, KPI-5 | `SELECT TOP 5 * FROM pbi.DailyInventorySnapshot` |
| 3 | Does Order_No join between ShipmentHeader and SalesHeader? | OTIF join | Verify format match |
| 4 | Posting_Date vs Shipment_Date for "actual ship date"? | OTIF on-time check | Andrew Wong confirmed Posting_Date = ship date |

---

## Card Design (from design_guide.html + d07-handoff.md)

**9-layer card layout (380x200px):**
1. Rectangle bg #FFF, border #E4C7DA 1px, corner radius 8px
2. Text box -- KPI name, 13px Bold #3F0938
3. Pill chip -- category (SERVICE/INVENTORY), filled #6F2365 or #E4C7DA
4. Card -- [KPI Delta Label], top-right, conditional color
5. Card -- [KPI Value] (Latest Month), 32px Bold #3F0938
6. Text box -- "TARGET" + [KPI Target], 9-11px #888888
7. Text box -- period label (YTD/MTD/MTO), 9px #6F2365
8. Card -- [KPI Value] (Current period), 11px #6F2365
9. Line chart -- sparkline, X=Date[Date], Y=[KPI Value] (Sparkline), target line

**Colors:**
- Royal Purple: #6F2365
- Rich Purple: #3F0938
- Pastel Purple: #E4C7DA (borders, chip bg)
- Egg Yellow: #FDB831
- Cream: #FFF8F1 (page background)
- Card: #FFFFFF

**Grid:** 2 rows x 3 columns
- Row 1: OTIF | On-Time Shipment | Fill Rate
- Row 2: Stockout FG | Stockout Ing | Req vs Promised

**Slicers:** Period Selection (YTD/MTD/MTO), Product Category (Level 1), Country

---

## BC API Production Credentials

| Parameter | Value |
|-----------|-------|
| Tenant ID | dc1d12bc-3f8d-4059-ad23-8f594cb4dae5 |
| Client ID | 6cdc1f98-bacb-4200-b484-9beca96faf7a |
| Company ID | dab2b5f8-7c90-ee11-817a-002248b32b5b |
| Environment | Production |
| Base URL | https://api.businesscentral.dynamics.com/v2.0/production/api/v2.0 |
| Secret file | /tmp/bcsecret.txt (on Mac mini) |

**Note:** Production access may need Shine Chen approval. Sandbox is `Copy_CRP_UAT`.

**Extraction script:** `data_extract/extract_d07_api.py` -- extracts 7 tables via OData API with pagination. Run: `cd data_extract && python3 extract_d07_api.py`
