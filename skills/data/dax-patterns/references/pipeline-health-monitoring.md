# Pipeline Health Monitoring — Kings Pastry

## Overview
Cron job template for monitoring data pipeline health across Kings Pastry data sources:
- Azure SQL (DataWarehousePBI)
- Business Central API (live extractions)
- Power BI Service (dataset refresh)
- Python ETL jobs (scheduled via GitHub Actions / Azure Functions)
- Shopify GraphQL API (not currently in scope)

## Monitoring Checklist

### 1. Azure SQL Data Freshness
Run via `query_runner.py --validate` or custom queries:

```sql
-- Core table row counts
SELECT 'SalesHeader' as tbl, COUNT(*) as rows FROM bc.SalesHeader
UNION ALL SELECT 'SalesLine', COUNT(*) FROM bc.SalesLine
UNION ALL SELECT 'SalesHeaderArchive', COUNT(*) FROM bc.SalesHeaderArchive
UNION ALL SELECT 'SalesLineArchive', COUNT(*) FROM bc.SalesLineArchive
UNION ALL SELECT 'Item', COUNT(*) FROM bc.Item
UNION ALL SELECT 'ItemCategory', COUNT(*) FROM bc.ItemCategory
UNION ALL SELECT 'Customer', COUNT(*) FROM bc.Customer
UNION ALL SELECT 'DailyInventorySnapshot', COUNT(*) FROM pbi.DailyInventorySnapshot
UNION ALL SELECT 'KPIConfig', COUNT(*) FROM pbi.KPIConfig
UNION ALL SELECT 'KPIConfig_Staging', COUNT(*) FROM pbi.KPIConfig_Staging;

-- Date ranges + staleness
SELECT 'SalesHeader' as tbl, MIN(PostingDate) as min_dt, MAX(PostingDate) as max_dt,
       DATEDIFF(day, MAX(PostingDate), GETDATE()) as days_stale FROM bc.SalesHeader
UNION ALL SELECT 'SalesHeaderArchive', MIN(PostingDate), MAX(PostingDate),
       DATEDIFF(day, MAX(PostingDate), GETDATE()) FROM bc.SalesHeaderArchive
UNION ALL SELECT 'DailyInventorySnapshot', MIN(SnapshotDate), MAX(SnapshotDate),
       DATEDIFF(day, MAX(SnapshotDate), GETDATE()) FROM pbi.DailyInventorySnapshot;

-- Field population checks
SELECT 'SalesLine' as tbl, COUNT(*) as total, COUNT(ShipmentDate) as has_ship
FROM bc.SalesLine
UNION ALL SELECT 'SalesLineArchive', COUNT(*), COUNT(ShipmentDate) FROM bc.SalesLineArchive;

-- KPIConfig integrity
SELECT * FROM pbi.KPIConfig;
SELECT * FROM pbi.KPIConfig_Staging;
```

### 2. Business Central API Extraction Status
Check latest extraction logs in `/Users/hdsolanop/projects/hdsolanop/Kings-pastry/data_extract/csv/`:

- `D02_EXTRACTION_LOG.md` — D02 OTIF (salesOrders, salesOrderLines)
- `D04_EXTRACTION_LOG.md` — D04 Production (itemLedgerEntries, items, categories)
- `D05_EXTRACTION_LOG.md` — D05 Procurement (purchaseReceipts, purchaseOrders, vendors)
- `D07_EXTRACTION_LOG.md` — D07 Warehouse (items, categories, shipments, receipts, ILE)

Expected: **Status = OK** for all tables, runs within last 24-48h.

### 3. Power BI Service Dataset Refresh
**Currently not automated** — requires Power BI REST API setup:

1. Register Azure AD app with Power BI permissions (Dataset.ReadWrite.All)
2. Configure service principal credentials
3. Query `/groups/{groupId}/datasets/{datasetId}/refreshes`

### 4. Python ETL Jobs (Scheduled)
**Currently NOT scheduled** — all extractions are manual scripts.
Required: Deploy GitHub Actions workflows or Azure Functions with cron triggers.

### 5. Anomaly Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| Data staleness | >24h | >48h |
| KPIConfig rows | <19 (staging count) | 0 |
| BC API extraction | Any table ERROR | Any table ERROR |
| Row count delta | >20% vs 7-day avg | >50% vs 7-day avg |
| Future dates in data | Any | Any |

## Alert Format (WhatsApp/Slack/Email)
```
🚨 PIPELINE ALERT — Kings Pastry
Source: Azure SQL / BC API / Power BI / ETL
Component: [table/job name]
Issue: [description]
Severity: 🔴 Critical / 🟡 Warning / 🔵 Info
Action: [specific remediation]
Timestamp: [ISO 8601]
```

## Automation Target
Deploy as GitHub Action cron job:
```yaml
on:
  schedule:
    - cron: '0 11 * * *'  # 06:00 CDT / 11:00 UTC
jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v1
        with: creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Install ODBC Driver 18
        run: |
          curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
          curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
          apt-get update
          ACCEPT_EULA=Y apt-get install -y msodbcsql18
      - name: Run health check
        run: |
          cd Kings-pastry/DataBase
          python3 query_runner.py --validate
      - name: Check extraction logs
        run: |
          # Check D02/D04/D05/D07 log timestamps
      - name: Send alert
        if: failure()
        run: |
          # WhatsApp/Slack webhook
```