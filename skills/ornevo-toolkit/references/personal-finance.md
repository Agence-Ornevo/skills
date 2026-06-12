# Personal Finance System — Technical Reference

> Source: `hdsolanop/personal-finance` repo, `CLAUDE.md` + `DASHBOARD_DOCS.md`
> Last synced: 2026-06-20

## Architecture

```
Bank/Card Statements (PDF/CSV) / Email notifications (Gmail)
        │
        ▼
   NocoDB (nocodb.hernansolano.com)  ← source of truth, raw COP transactions
        │                                    Email scanner cron → auto-insert (2x daily)
        ▼
   Sure (sure.hernansolano.com)  ← self-hosted Maybe fork, analysis + budgeting
        │                            NocoDB → Sure sync (ALL account types via POST /transactions)
        ▼
   Finance Health Dashboard (HTML artifact, Chart.js + AI assessment)
```

## Accounts

| Account | Sure ID | NocoDB Table | Currency | Type |
|---------|---------|--------------|----------|------|
| Davibank Ahorro 7428 | `8cdd10a9-d331-4356-8c04-672f1001954f` | `mvwdw0iez1rozpc` | COP | Savings |
| Davibank Bolsillo 9294 | `495b50c5-a440-4066-b621-550ccd30f6c4` | `mw6owcbdfhe0vbk` | COP | Savings |
| BlackCard (Mastercard Black) | `cbce4e2d-8c5a-4b7d-9332-b26931da4ab3` | `m90exg4qwf2q8mm` | EUR (Sure) / COP (NocoDB) | Credit Card |
| Addi (loan) | `d27632e3-2a77-4954-b35c-a186be3df20b` | `miavyhgghu0623v` | COP | Loan |
| Nequi 3195028956 | `e67fe7b4-8eb6-4421-8857-7cd62bd29fb0` | `mc8zvmc9354mkgu` | COP | Savings |
| Wallet COP (cash) | `2041e43b-e177-4f2f-9a6b-8d996cdb393d` | `mdc441kcrbkmqm6` | COP | Cash |
| Wise EUR | `18acc375-9036-436c-a4c9-ed0b29a84f1a` | — (no NocoDB table) | EUR | Savings |
| Wise USD | `79b487b6-1942-41d7-8da7-198f70341795` | — (no NocoDB table) | USD | Savings |

NocoDB base ID: `pk2utrwhkwgn08j`

## Sure API — Transaction Creation (UPDATED June 2026)

**`POST /api/v1/transactions` works for ALL account types** — credit_card, loan, AND depository.

| Endpoint | Old (broken) | New (working) |
|----------|-------------|---------------|
| Create transaction | `POST /accounts/{id}/transactions` → **404** | `POST /transactions` → ✅ All types |
| List transactions | `GET /accounts/{id}/transactions` → 404 | `GET /transactions?page=N&per_page=25` → filter by `account.id` |

**Amount format:** The Sure REST API **always stores amounts in EUR** regardless of account currency. You MUST convert COP→EUR before sending (divide by FX rate). The Sure UI uses a different internal API that handles native currency correctly.

| Account Type | POST endpoint | Amount format |
|-------------|---------------|---------------|
| `credit_card` (BlackCard) | `POST /transactions` | COP ÷ FX rate → EUR |
| `loan` (Addi) | `POST /transactions` | COP ÷ FX rate → EUR |
| `depository` (7428, 9294, Nequi, Wallet) | `POST /transactions` | COP ÷ FX rate → EUR |

**Sign convention:** positive = expense (outflow), negative = income (inflow)

## NocoDB MCP — Pagination & Auth

**Pagination:** The `mcp_nocodb_queryRecords` tool supports a `page` parameter:
```
mcp_nocodb_queryRecords(tableId=..., pageSize=100, page=2, sort=[...], fields=[...])
```

**Auth:** The MCP token (`xc-mcp-token`) is DIFFERENT from the NocoDB REST API token. They cannot be used interchangeably. The MCP server acts as a proxy — direct REST API calls with the MCP token return 401.

**Table schemas vary by account:**
- 7428/9294/Wallet: `Fecha`, `Descripción`, `Valor Débito`, `Valor Crédito`
- Nequi: `Fecha`, `Descripción`, `Valor` (single column: negative=expense, positive=income), `Saldo`

**Duplicate records:** CSV imports created triplicate records in NocoDB. Always dedup by (Fecha, Descripción, amount) before syncing to Sure.

## Decisions (June 2026)

| Question | Decision |
|----------|----------|
| ATM withdrawals | Transfer to Wallet COP. Old already-spent ones stay as expenses. |
| Addi PSE payments | Credit from savings account (money out to pay Addi debt) |
| Micro-fees (0.04 COP) and interest credits (2-4 COP) | INCLUDE all — be precise |
| RV POS reversals | Cancel/refund — match to original purchase by amount+date. Exclude from spending if net zero. |

## Import Status (as of 2026-06-20)

| Account | NocoDB Records | Sure Transactions | Coverage |
|---------|---------------|-------------------|----------|
| BlackCard | ~327 | 15 (synced) | Apr 2025 – Jun 2026 |
| Davibank 7428 | ~655 (many dups) | 34 (page 1 synced) | through Jun 2026 |
| Davibank Bolsillo 9294 | ~21 | 9 (synced) | through Jun 2026 |
| Addi | ~8+ | Synced via API | Feb–Jun 2026 |
| Nequi | ~467+ | 92 (page 1 synced) | 2025 full year + 2026 |
| Wallet COP | ~21+ | 0 (pending) | through May 2026 |
| Wise EUR/USD | — | Via Sure balance only | — |

**Backfill progress:** 135 transactions synced (9294: 9, 7428p1: 34, Nequi p1: 92). Remaining: ~500-600 unique records across 7428p2-6, Nequi p2-4, Wallet COP.

**Total Sure transactions: 1,735+ across 70+ pages (as of Jun 20, 2026)**

## Key Rules

### NocoDB columns
- Davibank / BlackCard / Addi: `Fecha`, `Descripción`, `Valor Débito` (outflow), `Valor Crédito` (inflow)
- Nequi: `Fecha` (YYYY/MM/DD), `Descripción`, `Valor` (positive=inflow, negative=outflow), `Saldo`
- Max 10 records per `createRecords` batch

### Sure API
- Sign convention: **positive amount = expense**, negative = income
- Always include `category_id` — transactions without it show as Uncategorized
- BlackCard transactions must be converted **COP → EUR** using monthly average rates
- `GET /api/v1/transactions` has hard max of 25 per page — always paginate
- `signed_amount_cents` field = signed amount in cents (use this for calculations)
- `amount_cents` = absolute value in cents

### Statement extraction (BlackCard PDFs)
- **Include:** "Tus compras y avances" (current period only) + "Otros cargos" (SEGURO DE VIDA, 4XMIL, COMISIÓN AVANCE)
- **Exclude:** "Transacciones de periodos anteriores", CANCELADA entries, REINTEGRO entries, "Tus pagos y abonos"

### Transfer detection in calculations
- Exclude transfers from income/expense calculations (`tx["transfer"] is not None`)
- Exclude REDIFERIDO entries (CC balance restructurings)
- Sign convention for expense classification:
  - Depository: negative = expense; positive = income
  - Credit card: negative = expense (purchase); positive = SKIP (payment)
  - Loan: positive = expense (installment); negative = SKIP (disbursement)

## COP/EUR Monthly Exchange Rates (historical)

| Month | Rate (COP/EUR) |
|-------|---------------|
| Jan 2025 | ~4,800 (approximate) |
| Feb 2025 | ~4,800 (approximate) |
| Mar 2025 | ~4,800 (approximate) |
| Apr 2025 | 4,879.44 |
| May 2025 | 4,700.80 |
| Jun 2025 | 4,783.18 |
| Jul 2025 | 4,677.28 |
| Aug 2025 | 4,722.17 |
| Sep 2025 | 4,569.92 |
| Oct 2025 | 4,559.78 |
| Nov 2025 | 4,366.22 |
| Dec 2025 | 4,466.57 |
| Jan 2026 | 4,466.57 |
| Feb 2026 | 4,466.57 |
| Mar 2026 | 4,466.57 |
| Apr 2026 | 4,466.57 |
| May 2026 | 4,600.00 |
| Jun 2026 | 4,600.00 |

**Hardcoded FX in scripts:** EUR=4,600 COP, USD=4,200 COP

## Sure Category IDs

| Category | ID |
|----------|----|
| Transportation | `d0ffa2e2-9495-422a-9ba8-907ee9e2c190` |
| Food & Drink | `56629d0b-c018-4882-b01f-8330fe422a25` |
| Entertainment | `da3a9121-8667-4f8b-8f1c-40f6a50deaa2` |
| Subscriptions | `562aec1b-4d1a-4db1-92af-2171e7b189a2` |
| Shopping | `6712ef2d-99e8-456c-937a-bf884d52e14d` |
| Groceries | `f74e0067-eec2-4d8d-9a35-3cef4832ad38` |
| Travel | `71e92364-1670-427f-b3f4-17ef2b3f3c60` |
| Healthcare | `0bf94877-5f99-41b4-850e-2ea7c8c91064` |
| Insurance | `a37cc30d-0b5e-4ff6-a740-26e4e2e6e057` |
| Fees | `16fb88e5-1438-4403-9b06-868151cd04e9` |
| Services | `6dd61515-97af-4834-800c-487c878c1de4` |
| Personal Care | `5bfdc34c-e28a-483c-ae7f-7506f989a2bd` |
| Income | `82e37f10-43fe-4fcb-a8ee-5d66a5d6d2d7` |
| Loan Payments | `433520c4-ad8a-41ee-83ae-92c951c0e5da` |
| Savings & Investments | `e0b9806f-00de-4669-8530-95245a6d8cbc` |
| Child support | `a8d73307-cf04-443c-988d-0ea28842121a` |
| Gifts & Donations | `38102800-dc76-4b0f-85df-9604f1c70134` |
| Home Improvement | `ee262dc9-da86-48f6-aee0-74a89c522f85` |
| Investment Contributions | `8ed6640b-af56-44fc-b676-3dac4ad939f1` |
| Mortgage/Rent | `01b0a7f1-43f5-4e3f-87fd-35db67b1388e` |
| Sports & Fitness | `8642aab9-bc6c-490b-a8f0-a22707a33570` |
| Taxes | `5f199214-d54e45af-be59-dbfa0db3feb3` |
| Utilities | `6c087379-458b-4631-85db-5efa0c9f2d05` |

## Known Merchant Mappings

| Merchant pattern | Category |
|-----------------|----------|
| DIDI, DLO*DIDI, DL*DIDI RIDES, BOLT.EU, TEMBICI | Transportation |
| DIDI FOOD, DIDI CO FOOD, RAPPI (food order) | Food & Drink |
| NETFLIX, HBOMAX, SPOTIFY, CINE COLOMBIA, CINEMACITY | Entertainment |
| APPLE.COM/BILL, PARTNERS TELECOM, HELP.MAX, GODADDY, INTCH | Subscriptions |
| LATAM AIRLINES, ROYAL CARIBBEAN, TURISM WEB EBANX | Travel |
| TIENDAS ARA, TIENDA D1, JUMBO, EXITO, LACTEOS, BBC BODEGA | Groceries |
| COMPANIA DE MEDICINA | Healthcare |
| SEGURO DE VIDA OBLIGATORIO | Insurance |
| 4XMIL, COMISION AVANCE, 4 X 1000 | Fees |
| BELLA PIEL | Personal Care |
| TRIBUTI, FIXMYAPPLES | Services |
| LLAVE / UNERGY rendimientos | Income |
| PAGO PSE $499,100 mensual | Healthcare (planilla seguridad social) |
| BREB entries (Davibank) | Services |
| OPENROUTER, INC | Subscriptions |

## Dashboard Health Score (5 components × 20%)

| Component | Scoring Logic (simplified) |
|-----------|---------------------------|
| **Net Worth** | positive = 20, negative = 0 |
| **Emergency Fund** | ≥6mo = 20, ≥3 = 15, ≥1 = 10, <1 = 5 |
| **Savings Rate** | >20% = 20, >10% = 15, >5% = 10, >0 = 5, ≤0 = 0 |
| **Debt-to-Income** | <20% = 20, <35% = 15, <50% = 10, ≥50% = 5 |
| **Cash Flow** | positive = 20, negative = 0 |

Score labels: 80+ Excellent · 60–79 Good · 40–59 Fair · 20–39 Needs Attention · <20 Critical

## Critical Technical Notes

- Sure API: `GET /api/v1/transactions` hard max 25 per page regardless of `per_page` param
- Sure uses Entry IDs in web routes vs Transaction IDs in API — different UUIDs
- Transfer linking: `POST /transactions/:entry_id/transfer_match`
- Transfer UNLINKING: `DELETE /transfers/:transfer_id` — opaqueredirect = success
- Addi loan payments are tagged as transfers in Sure → use ALL transactions (not filtered) for Addi payment calculations
- Partial month savings rate: if current month in progress, use previous complete month
- BlackCard CC balance history: reconstruct backwards from current balance using monthly net change (exclude REDIFERIDO)
- For large Sure imports (100+ txs): use `concurrent.futures.ThreadPoolExecutor(max_workers=8)`
- Sure API base: `https://sure.hernansolano.com/api/v1/`
- Auth header: `X-Api-Key: dd4d...`
- `amount_cents` is always positive; `signed_amount_cents` carries the sign
- `signed_amount_cents` uses the Sure sign convention (positive = expense)
- **NocoDB MCP token ≠ REST API token** — cannot use MCP token for direct REST calls
- **NocoDB duplicates:** CSV imports created triplicates. Dedup by (date, desc, amount) before sync.

## Email-to-NocoDB Pipeline

**Status:** Scanner script written (`~/.hermes/scripts/finance-email-scanner.py`), cron job active (2x daily: 8 AM, 8 PM)

**Confirmed email sources:**
| Sender | Account | Parser |
|--------|---------|--------|
| `DAVIbankInforma@davibank.com` | Davibank (7428/9294/BlackCard) | ✅ Implemented |
| `serviciopse@achcolombia.com.co` | PSE/ACH payments | ✅ Implemented |
| `somos@nequi.com.co` | Nequi | ✅ Implemented |
| `support@addi.com` | Addi | ✅ Implemented |
| `no-reply@remitly.com` | Remitly (Wise→DaviBank) | ✅ Implemented |
| TBD | Wise | Sender domain not yet confirmed |

**Dedup strategy:** hash of (date + account + amount + description) prevents re-insertion
**Transfer mapping:** PSE→Addi/Nequi + Remitly→Wise+7428 both recorded
**State tracking:** `~/.hermes/data/finance-scanner-state.json` tracks last-seen email IDs per sender
**Classification rules:** `~/.hermes/classification-rules.json` — 70+ merchant→category mappings

**Himalaya search syntax note:** `from X to Y` causes a parser error. Use `from X` separately.

## Files & Scripts

| File | Purpose |
|------|---------|
| `~/projects/hdsolanop/personal-finance/finance-health-dashboard.html` | Live dashboard HTML artifact |
| `~/.hermes/scripts/finance-email-scanner.py` | Email → NocoDB parser (5 sources) |
| `~/.hermes/scripts/finance-sure-sync.py` | NocoDB → Sure API sync script |
| `~/.hermes/scripts/backfill_depository.py` | One-time backfill from NocoDB JSON → Sure |
| `~/.hermes/classification-rules.json` | Merchant→category rules (70+ entries) |
| `~/.hermes/data/finance-scanner-state.json` | Scanner state (last-seen email IDs) |
| `~/projects/hdsolanop/personal-finance/CLAUDE.md` | Full project instructions |
| `~/projects/hdsolanop/personal-finance/DASHBOARD_DOCS.md` | Dashboard documentation |

## Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Sure API | `https://sure.hernansolano.com` | Finance app (self-hosted Maybe) |
| NocoDB | `https://nocodb.hernansolano.com` | Transaction database |

⚠️ Both are self-hosted on OVH B2-7. If the server goes down, the entire finance system breaks.

## NocoDB MCP Configuration

To enable MCP tools in Hermes, add to `~/.hermes/config.yaml` under `mcp_servers:`:

```yaml
  nocodb:
    command: "npx"
    args:
      - "mcp-remote"
      - "https://nocodb.hernansolano.com/mcp/<ncId>"
      - "--header"
      - "xc-mcp-token: <token>"
    connect_timeout: 60
    timeout: 120
```

**Note:** The agent cannot edit `config.yaml` directly (security block). Hernan must add this manually.

**Capabilities:** Record-level CRUD on NocoDB tables. Does NOT handle schema/metadata changes.
**Security:** Token grants full CRUD access. Never commit to source control.
**Pagination:** Use `page` parameter in `mcp_nocodb_queryRecords` (not `offset`).

## Key Metrics (as of Jun 20, 2026)

| Metric | Value |
|--------|-------|
| Net Worth | 123.5M COP |
| Total Assets | 166.2M COP |
| Total Liabilities | 42.7M COP |
| Health Score | 100/100 |
| Savings Rate (May 2026) | 30.1% |
| Emergency Fund | 23.5 months |
| DTI | 1.0% |
| Addi Payoff | 3 months remaining |
| BlackCard Balance | 41.2M COP (EUR) |
| Currency Exposure | 99% EUR |
| Backfill Progress | 135/600+ transactions synced |
