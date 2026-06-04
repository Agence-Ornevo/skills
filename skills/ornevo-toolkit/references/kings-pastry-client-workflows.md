# Kings Pastry — Client Email Templates & Workflows

## Cross-Dashboard Client Questions Workflow

When extracting questions and TODO items from multiple dashboard docs for a client email:

### Source Files (in repo)
- `Open_Items_Client_and_Shine.md` — Master tracker, questions by owner (Shine/Client/Ornevo)
- `D0X_Data_Source_Synthesis.md` — Per-dashboard KPI data source matrices
- `D0X_Data_Source_Connection_List.md` — BC table connection details, blockers
- `D0X_KPI[N]_[Name]_Data_Sources.md` — Per-KPI data source details
- `V2_Out_of_Scope_Tracker.md` — Deferred items, post-build trail
- `Client_Data_Questions.docx` — Client requirements doc (V2.0)

### Extraction Pattern
1. Read Open_Items_Client_and_Shine.md first (master index)
2. Read per-dashboard data source docs for the specific dashboards requested
3. Read per-KPI data source docs for blocked KPIs
4. Consolidate into structured document with sections per dashboard
5. Format: Question | Owner | KPIs Affected | Priority
6. Group by audience: For Shine (data/IT), For Client (functional owners), For Ornevo/Manuel
7. Create master cross-dashboard summary table at the end

### Email Structure
- Opening: State phase (testing/build) and purpose
- Per-dashboard: CRITICAL items first, then HIGH
- Each item: #, question, what's needed, who owns it
- End with: Build order + call to action for priority responses
- Keep email body to 1 page; full detail in attached doc

### Output Format Preference
- **ALL emails and client deliverables in English only**
- Bullet points, not paragraphs
- Action items with clear owners
- Priority markers: 🔴 CRITICAL | 🟡 HIGH | 🟢 MEDIUM

## Key Stakeholders (Kings Pastry)

| Name | Role | Engagement |
|------|------|-----------|
| Andrew Wong | Manufacturing + OTIF definition | On-time tolerance, production planning |
| Henry Lam | Customer Service | Req vs Promised dates, delivery tolerance |
| Martin Huang | Finance | GL account mappings, cost buckets, labour accounts |
| Patrick Lam | Logistics / Warehouse | Capacity, bin structure, physical count process |
| Anson Lam | Supply Chain / Procurement | Stockout calculations, BOM, forecast |
| Dickie Dik | Production Planning | BOM, production orders, WIP |
| Shine (IT) | BC admin, data access | All BC endpoint, mapping, and export questions |
| Manuel Robles (MR) | Power BI developer | All build execution |

## Priority Dashboard Build Order (current as of Jun 3)

### D07 (Warehouse Operations) — IN TESTING
Manual build: Pick Accuracy → Capacity → Inv Integrity → Labour (blocked on Shine)

### D02 (Service & Fulfillment)  
Manuel build: KPI-6 Req/Prom → KPI-3 Fill Rate → KPI-2 On-Time → KPI-1 OTIF → KPI-4 Stockout FG → KPI-5 Stockout Ing

### D05 (Procurement & Supplier Performance)
Manuel build: KPI-4 Spend Exposure → KPI-1 PO Adherence → KPI-2 Lead-Time → KPI-3 PPV
