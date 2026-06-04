# Personal Finance System — Technical Reference

> Source: `hdsolanop/personal-finance` repo, `CLAUDE.md` + `DASHBOARD_DOCS.md`
> Last synced: 2026-06-17

## Architecture

```
Bank/Card Statements (PDF/CSV)
        │
        ▼
   NocoDB (nocodb.hernansolano.com)  ← source of truth, raw COP transactions
        │
        ▼
   Sure (sure.hernansolano.com)  ← self-hosted Maybe fork, analysis + budgeting
        │
        ▼
   Finance Health Dashboard (HTML artifact, Chart.js + Claude Haiku AI)
```

## Accounts

| Account | Sure ID | Currency | Type |
|---------|---------|----------|------|
| Davibank Ahorro 7428 | `8cdd10a9-d331-4356-8c04-672f1001954f` | COP | Savings |
| Davibank Bolsillo 9294 | `495b50c5-a440-4066-b621-550ccd30f6c4` | COP | Savings |
| BlackCard (Mastercard Black) | `cbce4e2d-8c5a-4b7d-9332-b26931da4ab3` | EUR/COP | Credit Card |
| Addi (loan) | `d27632e3-2a77-4954-b35c-a186be3df20b` | COP | Loan |
| Nequi 3195028956 | `e67fe7b4-8eb6-4421-8857-7cd62bd29fb0` | COP | Savings |
| Wallet COP (cash) | `2041e43b-e177-4f2f-9a6b-8d996cdb393d` | COP | Cash |
| Wise EUR | `18acc375-9036-436c-a4c9-ed0b29a84f1a` | EUR | Savings |
| Wise USD | `79b487b6-1942-41d7-8da7-198f70341795` | USD | Savings |

NocoDB base ID: `pk2utrwhkwgn08j`

## Import Status (as of 2026-05-27)

| Account | Records | Coverage |
|---------|---------|----------|
| BlackCard | 311 | Apr 2025 – May 22 2026 |
| Davibank 7428 | 92 | through May 25 2026 |
| Davibank Bolsillo 9294 | 18 | through May 21 2026 |
| Wise EUR | 489 | through May 22 2026 |
| Wise USD | 489 | through May 22 2026 |
| Addi | 8 installments | Feb–May 2026 |
| Nequi | 467 | 2025 full year + Jan–Apr 2026 |
| Wallet COP | 21 | through May 24 2026 |

## Key Rules

### NocoDB columns
- Davibank / BlackCard / Addi: `Fecha`, `Descripción`, `Valor Débito` (outflow), `Valor Crédito` (inflow)
- Nequi: `Fecha` (YYYY-MM-DD), `Descripción`, `Valor` (positive=inflow, negative=outflow), `Saldo`
- Max 10 records per `createRecords` batch

### Sure API
- Sign convention: **positive amount = expense**, negative = income
- Always include `category_id` — transactions without it show as Uncategorized
- BlackCard transactions must be converted **COP → EUR** using monthly average rates
- `GET /api/v1/transactions` has hard max of 25 per page — always paginate

### Statement extraction (BlackCard PDFs)
- **Include:** "Tus compras y avances" (current period only) + "Otros cargos" (SEGURO DE VIDA, 4XMIL, COMISIÓN AVANCE)
- **Exclude:** "Transacciones de periodos anteriores", CANCELADA entries, REINTEGRO entries, "Tus pagos y abonos"

### ATM withdrawals = transfers to Wallet COP
Any `RETIRO ATM` entry must be recorded as a transfer to Wallet COP in both Sure and NocoDB.

## COP/EUR Monthly Exchange Rates (historical)

| Month | Rate (COP/EUR) |
|-------|---------------|
| Apr 2025 | 4,879.44 |
| May 2025 | 4,700.80 |
| Jun 2025 | 4,783.18 |
| Jul 2025 | 4,677.28 |
| Aug 2025 | 4,722.17 |
| Sep 2025 | 4,569.92 |
| Oct 2025 | 4,559.78 |
| Nov 2025 | 4,366.22 |
| Dec 2025 | 4,466.57 |

Source: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{YYYY-MM-DD}/v1/currencies/eur.json`

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
| Fees | `16fb88e5-1438-4403-9b06-868151cd0e94` |
| Services | `6dd61515-97af-4834-800c-487c878c1e64` |
| Personal Care | `5bfdc34c-e28a-483c-ae7f-7506f989a2bd` |
| Income | `82e37f10-43fe-4fcb-a8ee-5d66a5d6d2d7` |
| Loan Payments | `433520c4-ad8a-41ee-83ae-92c951c0e5da` |

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

## Dashboard Health Score (5 components × 20%)

| Component | Scoring Logic |
|-----------|--------------|
| **Net Worth** | >12mo income=100, >6=90, >3=75, >0=60, >-3=30, >-12=15, else=5 |
| **Emergency Fund** | ≥6mo expenses=100, ≥3=75, ≥1=40, ≥0.5=20, else=5 |
| **Savings Rate** | ≥20%=100, ≥15%=75, ≥10%=50, ≥5%=25, ≥0%=10, negative=0 |
| **Debt-to-Income** | <15%=100, <25%=80, <35%=60, <50%=40, <100%=20, else=5 |
| **Cash Flow** | ≥20%=100, ≥10%=65, ≥0%=35, negative=0 |

Score labels: 80+ Excellent · 60–79 Good · 40–59 Fair · 20–39 Needs Attention · <20 Critical

## Critical Technical Notes

- Sure API: `GET /api/v1/transactions` hard max 25 per page regardless of `per_page` param
- Sure uses Entry IDs in web routes vs Transaction IDs in API — different UUIDs
- Transfer linking: `POST /transactions/:entry_id/transfer_match`
- Transfer UNLINKING: `DELETE /transfers/:transfer_id` — opaqueredirect = success
- Addi loan payments are tagged as transfers in Sure → use `all_txs` (not filtered `txs`) for Addi calculations
- Partial month savings rate: if current month in progress, use previous complete month
- `window.cowork.askClaude(prompt, data[])` — `data[]` is for MCP tool results only, always pass `[]`; embed all text in prompt string
- BlackCard CC balance history: reconstruct backwards from current balance using monthly net change
- For large Sure imports (100+ txs): use `concurrent.futures.ThreadPoolExecutor(max_workers=8)`

## Files in Repo

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Full project instructions (168 lines) |
| `DASHBOARD_DOCS.md` | Dashboard documentation (299 lines) |
| `finance-health-dashboard.html` | Live dashboard HTML artifact |
| `financial_health_report.html` | Static report version |
| `backfill_exchange_rates.rb` | Exchange rate backfill script (Ruby) |
| `exchange_rates_backfill.sql` | SQL for exchange rate backfill |
| `wise_eur_import.csv` | Wise EUR transaction import CSV |
| `sync_git.bat` | Windows git sync script |

## Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Sure API | `https://sure.hernansolano.com` | Finance app (self-hosted Maybe) |
| NocoDB | `https://nocodb.hernansolano.com` | Transaction database |

⚠️ Both are self-hosted. If the server goes down, the entire finance system breaks. Set up health monitoring.
