# D02 Folder Index

The D02 Service & Fulfillment dashboard has a dedicated folder in the Kings-pastry repo:
`D02_Service_Fulfillment/`

## Folder Structure

```
D02_Service_Fulfillment/
  Build/
    D02_Build_Plan.md              <- Master build plan (OTIF-first approach)
    D02_Template_Analysis.md       <- Phase 0 output (fill from D07 V2 PBIX)
  Data_Sources/
    D02_Data_Source_Map.md         <- BC tables, pbi views, relationships, slicers
    D02_SQL_Queries.md             <- Pre-build validation queries
  DAX/
    D02_DAX_Measures.md            <- All 6 KPI measures + date table + calc group
    D02_Date_Table_DAX.md          <- Date table + calculation group DAX
  Documentation/
    D02_KPI_Definitions.md         <- KPI specs from wireframe V9 + spec V6
    D02_Slicer_Rules.md            <- Slicer applicability matrix
    D02_L2_L3_Grain.md             <- Detail table grain definitions
  Validation/
    D02_Validation_Checklist.md    <- SQL queries + DAX cross-checks
    D02_Data_Quality_Notes.md      <- Data quality notes
```

## Key Facts

- **Data source:** Azure SQL Data Warehouse (bc + pbi schemas), NOT BC OData
- **Template:** D07 Warehouse Operations V2.pbix (copy as starting point)
- **Build strategy:** OTIF first (validates data model), then cascade
- **Pre-built advantage:** pbi.DailyInventorySnapshot eliminates running balance calculations
- **Full build guide:** See references/kings-pastry-d02-build.md

## Build Order

1. OTIF (KPI-1) - validates SalesLine, SalesShipmentLine, SalesShipmentHeader join
2. On-Time Shipment (KPI-2) - same tables
3. Fill Rate (KPI-3) - same tables + Document_Date relationship
4. Req vs Promised (KPI-6) - bc.SalesHeader only (simplest)
5. Stockout FG (KPI-4) - pbi.DailyInventorySnapshot + FG code
6. Stockout Ingredients (KPI-5) - pbi.DailyInventorySnapshot + RAW code
