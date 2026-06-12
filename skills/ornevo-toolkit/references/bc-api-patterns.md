# BC API - Interaction Patterns & Gotchas

**Project:** Kings Pastry Control Tower
**Last verified:** 2026-06-03

---

## Authentication Gotcha: Special Characters in Client Secret

Azure AD client secrets may contain characters (tilde, underscore, plus, slash) that break Python string literals and shell interpolation.

**What breaks:**
- `python3 -c "..."` — shell interprets special chars
- Heredocs — some chars still get interpreted
- f-strings in Python — special chars inside expressions cause issues

**What works:**
- Store the secret in a file, read at runtime:
  ```python
  CLIENT_SECRET = open('path/to/secret.txt').read().strip()
  ```
- Use environment variables with the secret exported separately
- Base64-encode the secret, store encoded, decode at runtime

**Recommended pattern:**
```python
import os, urllib.request, urllib.parse, json

# Read secret from file to avoid shell/Python interpretation of special chars
# Store the secret file outside the repo at the persistent path
CLIENT_SECRET = open(os.path.expanduser('~/.hermes/kings-pastry/bc_secret.txt')).read().strip()

def get_token():
    data = urllib.parse.urlencode({
        'client_id': os.environ['BC_CLIENT_ID'],
        'client_secret': CLIENT_SECRET,
        'scope': 'https://api.businesscentral.dynamics.com/.default',
        'grant_type': 'client_credentials'
    }).encode()
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{os.environ['BC_TENANT']}/oauth2/v2.0/token",
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())['access_token']
```

### Zsh Heredoc Gotcha

Even with `<< 'DELIMITER'` (single-quoted), zsh can still interpret `~` in heredoc
content when the secret value contains it. The `~` in Azure AD secrets like
`V488Q~_YIFf...` gets expanded.

**Workaround:** Write the Python file using `cat > file << 'EOF'` from a bash shell,
or use `cp` to copy a known-good template and modify it. Avoid embedding the secret
value directly in any file — always read from a separate secret file at runtime.

---

## Line-Level Table Access Gotcha

BC API line-level tables **cannot be queried directly**:

```
WRONG:  GET /companies({id})/purchaseOrderLines  -> HTTP 400
Error: "You must specify an Id or a Document Id to get the lines."
```

**Correct pattern -- use navigation properties:**
```
RIGHT: GET /companies({id})/purchaseOrders({po_id})/purchaseOrderLines
RIGHT: GET /companies({id})/salesOrders({id})/salesOrderLines
RIGHT: GET /companies({id})/salesInvoices({id})/salesInvoiceLines
RIGHT: GET /companies({id})/journals({id})/journalLines
```

**Extraction strategy:**
1. First extract headers (with date filter)
2. Then extract lines per header via navigation

---

## NOT Available via Standard API (Kings Pastry, Jun 2026)

These tables require custom API pages or manual export:

| BC Table | Table # | Impact |
|----------|---------|--------|
| Bin | 7354 | Capacity KPI |
| Warehouse Entry | 7312 | Pick accuracy |
| Value Entry | 5802 | Labour KPI |
| Sales Header Archive | 5107 | Historical orders |
| Sales Line Archive | 5108 | Historical orders |
| Work Center | 99000760 | V2 blocker |
| Production BOM Header | 99000771 | V2 blocker |
| Production BOM Line | 99000772 | V2 blocker |

Check `/entityDefinitions` to see if new custom APIs have been added.

### Sales Order Archive — Custom API Endpoints NOT Available

Despite being documented as needed (SalesHeaderArchive 5107, SalesLineArchive 5108),
the following custom endpoints were tested and all return HTTP 404:

- `SalesOrderArchives` — 404
- `SalesOrderArchivedLines5160` — 404
- `SalesOrderArchiveLines` — 404
- `SalesLineArchives` — 404
- `SalesOrderLineArchives` — 404
- `SalesOrderArchivedLines` — 404
- `SalesLineArchive` — 404

The `/entityDefinitions` endpoint confirms **zero custom API pages** are published —
all 87 entity sets come from the standard Microsoft API.

**Action:** These tables must be exported manually from BC (web client or Excel).
If the BC admin publishes custom API pages in the future, re-test with `/entityDefinitions`.

### Full Verified Entity List (87 entities, Jun 2026)

The complete list of available entity sets is documented in the root endpoint response.
Key entities for D07: items, itemCategories, salesShipments, salesShipmentLines,
purchaseReceipts, purchaseReceiptLines, purchaseOrders, purchaseOrderLines,
salesOrders, salesOrderLines, salesInvoices, salesInvoiceLines, itemLedgerEntries,
generalLedgerEntries, accounts, dimensions, dimensionValues, locations, unitsOfMeasure,
itemVariants, vendors, customers, journals, journalLines, salespeoplePurchasers,
employees, timeRegistrationEntries, generalLedgerSetup, fixedAssets, projects,
bankAccounts, salesQuotes, salesQuoteLines, salesCreditMemos, salesCreditMemoLines,
purchaseCreditMemos, purchaseCreditMemoLines, opportunities, currencies, paymentMethods,
paymentTerms, shipmentMethods, taxGroups, taxAreas, countriesRegions, accountingPeriods,
currencyExchangeRates, disputeStatus, customerContacts, customerPayments,
customerPaymentJournals, vendorPayments, vendorPaymentJournal, applyVendorEntries,
agedAccountsReceivables, agedAccountsPayables, companyInformation, contacts,
contactsInformation, customerFinancialDetails, cashFlowStatements, balanceSheets,
incomeStatements, trialBalances, retainedEarningsStatements, dimensionSetLines,
documentAttachments, pictures, defaultDimensions, generalProductPostingGroups,
inventoryPostingGroups, attachments, pdfDocument, jobQueueEntries, jobQueueLogEntries,
fixedAssetLocations, customerSales, vendorPurchases.

---

## Pagination Pattern

```python
def bc_get_all(path, params=None):
    all_records = []
    url = BASE_V2 + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    while url:
        req = urllib.request.Request(url, headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        all_records.extend(data.get('value', []))
        url = data.get('@odata.nextLink')
    return all_records
```

### Pagination Gotcha: BC Omits `@odata.nextLink`

BC does **not** always return `@odata.nextLink` even when there are more pages.
If a full page (e.g., 1000 records) is returned without `nextLink`, the script
must fall back to `$skip` offset pagination:

```python
def bc_get_all_with_fallback(path, params=None, page_size=1000):
    all_records = []
    url = BASE_V2 + path
    params = dict(params or {})
    params['$top'] = page_size
    skip = 0
    while True:
        params['$skip'] = skip
        page_url = url + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(page_url, headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read())
        batch = data.get('value', [])
        all_records.extend(batch)
        next_link = data.get('@odata.nextLink')
        if next_link:
            # Use nextLink for subsequent pages (BC sometimes provides it)
            url = next_link
            params = None  # nextLink includes all params
            skip = 0
            continue
        if len(batch) < page_size:
            break  # Last page
        skip += page_size  # Fallback: manual offset
    return all_records
```

**Verified on:** itemLedgerEntries (224,603 records, 225 pages via `$skip`).

---

## Line Table Filtering Gotcha: `in` Operator Not Supported

BC returns **HTTP 501** for OData `in` operator:

```
WRONG: $filter=documentId in (id1, id2, id3)  -> HTTP 501
```

**Correct pattern — batched `or` conditions:**

```python
def filter_by_ids(field, ids, batch_size=15):
    """Build $filter with batched OR conditions for BC API."""
    batches = [ids[i:i+batch_size] for i in range(0, len(ids), batch_size)]
    filters = []
    for batch in batches:
        conditions = ' or '.join([f"{field} eq '{id}'" for id in batch])
        filters.append(f"({conditions})")
    return ' or '.join(filters)

# Usage: $filter=(documentId eq 'a') or (documentId eq 'b') or ...
```

**Verified on:** salesShipmentLines, purchaseReceiptLines (batch size 15 keeps URLs under BC limits).

---

## Date Filtering

| Table | Date Field | Example Filter |
|-------|------------|----------------|
| purchaseOrders | orderDate | $filter=orderDate ge 2025-01-01 |
| purchaseReceipts | postingDate | $filter=postingDate ge 2025-01-01 |
| salesOrders | orderDate | $filter=orderDate ge 2025-01-01 |
| salesShipments | postingDate | $filter=postingDate ge 2025-01-01 |
| itemLedgerEntries | postingDate | $filter=postingDate ge 2025-01-01 |
| generalLedgerEntries | postingDate | $filter=postingDate ge 2025-01-01 |

---

## Manual Export File Formats (Jun 2026)

### Warehouse Entry — Tab-Delimited TXT

BC Web Client exports Warehouse Entry as a **tab-delimited .txt file** (~109 MB, 425K rows).

**Format characteristics:**
- Tab-separated, UTF-8 encoding
- 36 columns: Entry_No, Entry_Type, Journal_Batch_Name, Line_No, Location_Code, Expiration_Date, Zone_Code, Bin_Code, Item_No, Description, Variant_Code, Quantity, Qty_Base, Unit_of_Measure_Code, Serial_No, Lot_No, Package_No, Qty_per_Unit_of_Measure, Source_Type, Source_Subtype, Source_Document, Source_No, Source_Line_No, Source_Subline_No, Reason_Code, No_Series, Cubage, Weight, Journal_Template_Name, Whse_Document_Type, Whse_Document_No, Registering_Date, User_ID, SystemModifiedAt31572, SystemModifiedBy37920, ETag
- Date format: `"Friday, May 1, 2026"` (long date) and `"05/01/2026 5:38:41 PM"` (datetime)
- Line endings: `\r\n` (Windows-style)
- No header quoting — raw tab-separated

**Conversion to CSV:**
```python
import csv
with open('Warehouse_entry.txt', 'r', encoding='utf-8') as infile, \
     open('warehouse_entry.csv', 'w', newline='', encoding='utf-8-sig') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile)
    for row in reader:
        writer.writerow(row)
```

### Sales Archive — Excel Format

BC Web Client exports Sales Order Archives as **.xlsx files**.

**SalesHeaderArchive.xlsx → sales_header_archive.csv:**
- 3,366 rows, 36 columns
- Key fields: Document_Type, No, Doc_No_Occurrence, Version_No, Date_Archived, Time_Archived, Archived_By, Interaction_Exist, Sell_to_Customer_No, Sell_to_Customer_Name, External_Document_No, Posting_Date, Shortcut_Dimension_1_Code, Shortcut_Dimension_2_Code, Location_Code, Salesperson_Code, Currency_Code, Document_Date, Requested_Delivery_Date, Payment_Terms_Code, Due_Date, Shipment_Method_Code, Shipment_Date, ETag

**SalesLineArchive.xlsx → sales_line_archive.csv:**
- 20,558 rows, 77 columns
- Key fields: Document_Type, Document_No, Doc_No_Occurrence, Version_No, Line_No, Type, No, Item_Reference_No, Variant_Code, Description, Location_Code, Quantity, Unit_of_Measure_Code, Unit_Price, Line_Amount, Line_Discount_Percent, Qty_to_Ship, Quantity_Shipped, Qty_to_Invoice, ETag

**Conversion to CSV (openpyxl):**
```python
import openpyxl, csv

def excel_to_csv(xlsx_path, csv_path):
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header = [str(c) if c is not None else '' for c in rows[0]]
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows[1:]:
            writer.writerow([str(c) if c is not None else '' for c in row])
```

---

## Labour KPI — ADP Report Data Flow

**Source:** `Labor Cost Master ADP.xlsx` from SharePoint
**URL:** `kingspastry17.sharepoint.com/sites/KingsPastry2/`

**Data flow:**
```
ADP Labor File (SharePoint)
  → ADP Dept Code
  → ENT-T07 Mapping Table (ADP Dept → BC Work Centre No.) ← BLOCKED on Shine
  → BC Work Centre (Table 99000760)
  → ValueEntry-5802 (filtered: FG category, 2026+) → Outbound Cases
  → Divide: Cases / Labour Hours = cs/lh
```

**Current status:** `v_D07_Labour` has 0 rows. Card shows BLANK until pipeline runs.

**Required mapping file:** `ADP_BC_work_centre_mapping.xlsx` (31 ADP dept codes → BC Work Centre No.)
- 12 provided, 19 remaining — task for Shine

**Filtering approach in pipeline:**
- ValueEntry-5802 filtered to FG items only (via ItemCategory join)
- Filtered to 2026+ to manage table size
- Mandatory filter: `Item_Ledger_Entry_Type = "Sales"` for outbound cases

---

## Credential Storage — Cross-Session Pattern

**NEVER embed credentials in scripts or commit to repo.**

### Persistent Secret Location

Store the BC client secret outside the repo in Hermes home:

```
~/.hermes/kings-pastry/bc_secret.txt   ← secret (chmod 600, never committed)
config/bc_api.env                        ← non-secret params (committed to repo)
data_extract/.env                        ← local override (gitignored)
```

### Project Config File (committed)

`config/bc_api.env` contains all non-secret BC API parameters:

```bash
BC_TENANT_ID=dc1d12bc-3f8d-4059-ad23-8f594cb4dae5
BC_CLIENT_ID=6cdc1f98-bacb-4200-b484-9beca96faf7a
BC_COMPANY_ID=dab2b5f8-7c90-ee11-817a-002248b32b5b
BC_SECRET_FILE=/Users/hdsolanop/.hermes/kings-pastry/bc_secret.txt
BC_BASE_URL=https://api.businesscentral.dynamics.com/v2.0/production/api/v2.0
```

### Usage in Python Scripts

```python
import os
from pathlib import Path

# Load non-secret config from project
config = {}
config_path = Path('config/bc_api.env')
if config_path.exists():
    for line in config_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            config[k.strip()] = v.strip()

# Read secret from persistent location
secret_file = config.get('BC_SECRET_FILE', '~/.hermes/kings-pastry/bc_secret.txt')
client_secret = open(os.path.expanduser(secret_file)).read().strip()
```

### Making API Available in a New Session

1. Ensure `~/.hermes/kings-pastry/bc_secret.txt` exists (create from memory if needed)
2. Load `config/bc_api.env` for connection parameters
3. Read secret from file at runtime — never hardcode
4. The project `CLAUDE.md` also documents the BC API connection for Hermes sessions

**Full credential values stored in agent memory, not in this file.**

---

## Verified Endpoints (tested 2026-06-04)

| Endpoint | BC Object | Status | Notes |
|----------|-----------|--------|-------|
| `items` | 27 | ✅ | 3,023 rows. Fields: number, displayName, itemCategoryCode, inventoryPostingGroupCode |
| `itemCategories` | 5722 | ✅ | 77 rows. Fields: code, displayName. No parent hierarchy — codes ARE Level 1 |
| `salesShipments` | 110 | ✅ | 6,218 rows. Fields: number, orderNumber, postingDate, customerNumber |
| `salesShipmentLines` | 111 | ✅ | 48,637 rows. Fields: documentNo, sequence, lineObjectNumber, quantity, shipmentDate |
| `purchaseReceipts` | 120 | ✅ | 12,578 rows |
| `purchaseReceiptLines` | 121 | ✅ | 19,401 rows |
| `itemLedgerEntries` | 32 | ✅ | 224,603 rows. Entry types: Output, Sale, Purchase, Consumption, Transfer, Positive Adjmt., Negative Adjmt. |
| `salesOrders` | 36 | ⚠ Partial | Header only. Has requestedDeliveryDate but NO promisedDeliveryDate. Lines endpoint returns 404. |
| `customers` | 18 | ✅ | Fields: number, displayName, country, state, postalCode, salespersonCode |

### D02-Specific API Notes

- **SalesOrder lines (37)**: NOT available via API. Use SQL DDBB bc.SalesLine instead.
- **SalesOrder promised date**: NOT on API SalesOrder header. Use SQL DDBB bc.SalesHeader[Promised_Delivery_Date].
- **SalesLine has all OTIF fields at line level**: ShipmentDate, PromisedDeliveryDate, QuantityShipped, Quantity — all confirmed in SQL DDBB.
- **Inventory Posting Groups** (from items.csv): FG, RAW, PKG, WIP, DIST, GS, OFFICE, CLEAN
- **Item Categories** (from item_categories.csv): 77 categories = Level 1 values (no parent hierarchy)
- **Order number join**: SalesShipments[orderNumber] → SalesHeader[No] — VERIFIED 1,632 matches in CSV data
- **DailyInventorySnapshot**: Pre-built pbi view. Columns: SnapshotDate, ItemNo, ItemCategory, Quantity (≤0 = stockout), StockIn, StockOut, LocationCode. NOT available via BC API — SQL only.
