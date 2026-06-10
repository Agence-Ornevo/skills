# D02 OTIF Date Field Analysis - Session Findings (2026-06-05)

## Problem Identified
During D02 Service & Fulfillment dashboard build, OTIF measures returned values only for specific dates due to missing ShipmentDate/PromisedDeliveryDate in live bc.SalesLine table.

## Client Documentation Evidence
From `Client_Data_Questions(1).docx`:
- BC Sales Line (Table 37) contains both Requested_Delivery_Date and Promised_Delivery_Date fields
- Both fields confirmed as actively maintained by KP sales team ("Both fields are used by KP sales team")
- OTIF definition: "depends on comparing the actual shipment date to the promised shipment date"

## Data Extraction Reality
- Live `bc.SalesLine`: ShipmentDate/PromisedDeliveryDate fields mostly blank
- Archive `bc.SalesLineArchive`/`bc.SalesHeaderArchive`: 20,558+ rows with dates populated

## Resolution Pattern
Use archive tables for date-critical KPIs requiring shipment/delivery dates:
- Replace `SalesLine` → `SalesLineArchive` 
- Replace `SalesHeader` → `SalesHeaderArchive`
- Use `Shipment_Date` and `Promised_Delivery_Date` fields (underscore naming)
- Maintain relationship: `SalesLineArchive[Document_No] → SalesHeaderArchive[No]`

## Verification Queries
```dax
-- Live table check
EVALUATE ROW(
    "Live_Total", COUNTROWS(SalesLine),
    "Live_Shipment_Pct", 
        DIVIDE(
            CALCULATE(COUNTROWS(SalesLine), NOT ISBLANK(SalesLine[ShipmentDate])),
            COUNTROWS(SalesLine)
        )
)

-- Archive table check  
EVALUATE ROW(
    "Archive_Total", COUNTROWS(SalesLineArchive),
    "Archive_Shipment_Pct",
        DIVIDE(
            CALCULATE(COUNTROWS(SalesLineArchive), NOT ISBLANK(SalesLineArchive[Shipment_Date])),
            COUNTROWS(SalesLineArchive)
        )
)
```

## When to Apply This Pattern
1. KPI requires historical shipment/delivery dates (OTIF, On-Time Shipment)
2. Live table date field exploration shows low population (<95%)
3. Archive tables contain complete historical data
4. Client confirms field maintenance and usage

## Related Files
- D02_Service_Fulfillment/Documentation/D02_OTIF_DateField_Analysis.md
- D02_Service_Fulfillment/Documentation/D02_Session_Summary_2026-06-05.md