# SQL Deduplication Patterns — Kings Pastry Archive Tables

## Archive Table Versioning

Archive tables (`bc.SalesHeaderArchive`, `bc.SalesLineArchive`) contain multiple versions per order/line, tracked by:
- `DateArchived` — date the record was archived
- `TimeArchived` — time the record was archived

**Verified counts (2026-06-06):**
- `bc.SalesHeaderArchive`: 59,873 rows, 28,870 orders have multiple versions (up to 10)
- `bc.SalesLineArchive`: 388,267 rows, 187,157 line items have multiple versions

---

## Pattern 1: Latest Version per Order (SalesHeaderArchive)

```sql
CREATE OR ALTER VIEW bc.SalesHeaderArchive_Deduped AS
WITH Ranked AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY [No] 
            ORDER BY [DateArchived] DESC, [TimeArchived] DESC
        ) as rn
    FROM bc.SalesHeaderArchive
    WHERE [No] IS NOT NULL AND [No] <> ''
)
SELECT *
FROM Ranked
WHERE rn = 1;
```

---

## Pattern 2: Latest Version per Line (SalesLineArchive)

```sql
CREATE OR ALTER VIEW bc.SalesLineArchive_Deduped AS
WITH LatestHeader AS (
    SELECT [No], [DateArchived], [TimeArchived]
    FROM bc.SalesHeaderArchive_Deduped
),
RankedLines AS (
    SELECT 
        sla.*,
        lh.[DateArchived] as Header_DateArchived,
        lh.[TimeArchived] as Header_TimeArchived,
        ROW_NUMBER() OVER (
            PARTITION BY sla.[DocumentNo], sla.[LineNo] 
            ORDER BY lh.[DateArchived] DESC, lh.[TimeArchived] DESC, sla.[LineNo]
        ) as rn
    FROM bc.SalesLineArchive sla
    LEFT JOIN LatestHeader lh ON sla.[DocumentNo] = lh.[No]
    WHERE sla.[DocumentNo] IS NOT NULL AND sla.[DocumentNo] <> ''
      AND sla.[LineNo] IS NOT NULL AND sla.[LineNo] <> 0
)
SELECT 
    sla.[DocumentNo], sla.[LineNo], sla.[No], sla.[Quantity], sla.[QuantityShipped],
    sla.[OutstandingQuantity], sla.[ShipmentDate], sla.[RequestedDeliveryDate],
    sla.[PromisedDeliveryDate], sla.[PlannedDeliveryDate], sla.[PlannedShipmentDate],
    sla.[ItemCategoryCode], sla.[CompletelyShipped]
FROM RankedLines sla
WHERE sla.rn = 1;
```

---

## Pattern 3: UNION Views (Current + Deduped Archive)

```sql
-- SalesHeader_Union
CREATE OR ALTER VIEW bc.SalesHeader_Union AS
SELECT 
    [No], [DocumentType], [SelltoCustomerNo], [PostingDate], [ShipmentDate],
    [RequestedDeliveryDate], [PromisedDeliveryDate], [DocumentDate], [Status],
    'Current' as SourcePeriod
FROM bc.SalesHeader
WHERE [No] IS NOT NULL AND [No] <> ''

UNION ALL

SELECT 
    [No], [DocumentType], [SelltoCustomerNo], [PostingDate], [ShipmentDate],
    [RequestedDeliveryDate], [PromisedDeliveryDate], [DocumentDate], [Status],
    'Archive' as SourcePeriod
FROM bc.SalesHeaderArchive_Deduped;

-- SalesLine_Union
CREATE OR ALTER VIEW bc.SalesLine_Union AS
SELECT 
    [DocumentNo], [LineNo], [No], [Quantity], [QuantityShipped], [OutstandingQuantity],
    [ShipmentDate], [RequestedDeliveryDate], [PromisedDeliveryDate],
    [PlannedDeliveryDate], [PlannedShipmentDate], [ItemCategoryCode],
    [CompletelyShipped],
    'Current' as SourcePeriod
FROM bc.SalesLine
WHERE [DocumentNo] IS NOT NULL AND [DocumentNo] <> ''
  AND [LineNo] IS NOT NULL AND [LineNo] <> 0

UNION ALL

SELECT 
    [DocumentNo], [LineNo], [No], [Quantity], [QuantityShipped], [OutstandingQuantity],
    [ShipmentDate], [RequestedDeliveryDate], [PromisedDeliveryDate],
    [PlannedDeliveryDate], [PlannedShipmentDate], [ItemCategoryCode],
    [CompletelyShipped],
    'Archive' as SourcePeriod
FROM bc.SalesLineArchive_Deduped;
```

---

## Verification Queries

```sql
-- Row counts
SELECT 'SalesHeader_Union' as TableName, COUNT(*) as Rows FROM bc.SalesHeader_Union
UNION ALL
SELECT 'SalesLine_Union', COUNT(*) FROM bc.SalesLine_Union
UNION ALL
SELECT 'SalesHeaderArchive_Deduped', COUNT(*) FROM bc.SalesHeaderArchive_Deduped
UNION ALL
SELECT 'SalesLineArchive_Deduped', COUNT(*) FROM bc.SalesLineArchive_Deduped;

-- Verify no duplicates in UNION
SELECT 'SalesHeader_Union' as TableName, COUNT(*) as DuplicateGroups
FROM (
    SELECT [No], COUNT(*) as cnt
    FROM bc.SalesHeader_Union
    GROUP BY [No]
    HAVING COUNT(*) > 1
) t
UNION ALL
SELECT 'SalesLine_Union', COUNT(*)
FROM (
    SELECT [DocumentNo], [LineNo], COUNT(*) as cnt
    FROM bc.SalesLine_Union
    GROUP BY [DocumentNo], [LineNo]
    HAVING COUNT(*) > 1
) t;

-- Verify zero Current/Archive overlap
SELECT 'Header Overlap' as CheckName, COUNT(*) as OverlapCount
FROM (
    SELECT [No] FROM bc.SalesHeader_Union WHERE SourcePeriod = 'Current'
    INTERSECT
    SELECT [No] FROM bc.SalesHeader_Union WHERE SourcePeriod = 'Archive'
) t
UNION ALL
SELECT 'Line Overlap', COUNT(*)
FROM (
    SELECT [DocumentNo], [LineNo] FROM bc.SalesLine_Union WHERE SourcePeriod = 'Current'
    INTERSECT
    SELECT [DocumentNo], [LineNo] FROM bc.SalesLine_Union WHERE SourcePeriod = 'Archive'
) t;
```

---

## Expected Row Counts (Post-Dedup)

| View | Expected Rows |
|------|---------------|
| `SalesHeader_Union` | ~60,176 (146 Current + 59,873 Archive - 12 overlap - 169 empty filtered) |
| `SalesLine_Union` | ~391,043 (950 Current + 388,267 Archive - 171 overlap - 1,807 empty filtered) |

---

## Key Findings (2026-06-06)

| Finding | Impact |
|---------|--------|
| Archive column names = PascalCase, **identical to current** | Clean UNION, no renaming needed |
| `SalesLineArchive[ShipmentDate]` = **99.96% populated** | Full OTIF history unblocked |
| Archive has **multiple versions** per order/line | Must dedup by `DateArchived` + `TimeArchived` |
| Current tables have **empty PKs** (169 headers, 1,807 lines) | Filter out before UNION |
| Current/Archive overlap: 12 headers, 171 lines | Prefer Current in dedup |

---

## Recommended: SQL Views Over Power Query M

| Aspect | Power Query M | SQL Views |
|--------|---------------|-----------|
| Scope | Single PBIX | All dashboards (D01-D08) |
| Maintenance | Per PBIX | Single source of truth |
| Performance | PBIX refresh | Pre-computed in DB |
| Version Control | In PBIX | In Git |
| Refresh | Manual | ADF pipeline |

**Run:** `D02_SQL_Deduplication.sql` in Azure SQL → creates 4 views → import UNION views in Power BI.