# D05 – Procurement & Supplier Performance Dashboard (Kings Pastry)

## Latest Wireframe (ControlTowerV9.html)
- Primary KPI: **Inbound PO Adherence %** (combines timing & quantity tolerance)
- Definition: % of PO lines received **on or before** confirmed/requested date **AND** within quantity tolerance (ordered ≤ received ≤ ordered × 1.05).

## Sub‑metrics displayed on the KPI card
| Sub‑metric | Meaning |
|------------|---------|
| Timing Adherence % | % of PO lines received on/before confirmed/requested date |
| Quantity Adherence % | % of PO lines with received quantity inside the tolerance band |
| Late PO Lines | Count of PO lines where receipt date > confirmed/requested date |
| Short/Over Delivered PO Lines | Count of PO lines where received quantity < ordered or > ordered × 1.05 |
| At‑Risk Open POs | Number of open POs projected to miss timing or quantity adherence |

## Required Business Central tables
| Table (ID) | Purpose |
|------------|---------|
| PurchaseHeader‑38 | order date, confirmed/requested (promised) delivery date |
| PurchaseLine‑39 | ordered quantity (and PO unit price if PPV added later) |
| PurchRcptHeader‑120 | receipt date (actual receipt) |
| PurchRcptLine‑121 | received quantity |
| Item‑27 | UOM (optional, for detail table) |
| ItemCategory‑5722 | Level 1 parent category – **required slicer** |
| Vendor‑23 | optional – supplier dimension in drill‑down |
| PurchaseHeaderArchive‑5109 / PurchaseLineArchive‑5110 | only if you need prior‑year values for the YTD vs prior‑year comparison shown on the KPI card |

## Slicers applicable to D05
| Slicer | Status | Details |
|--------|--------|---------|
| Product Category (Level 1 from ItemCategory‑5722) | **Required** | Use Level 1 parent category; if multiple hierarchy levels exist, aggregate them to the parent before slicing. |
| Vendor‑23 | Optional | Can be added as a dimension in the drill‑down table. |
| Channel | **Not applicable** | Channel lives on the customer card only. |
| Region | **Not applicable** | Region lives on the customer/ship‑to address only. |

## Notes & Constraints
- Tolerance is fixed at **+5 %** (no vendor‑specific band).
- Lead‑time is **item‑level** (stored on Item table) – not needed for the current KPI.
- The current wireframe does **not** show separate KPIs for OTD, IFD, PPV, lead‑time variance, or a composite supplier score.
- Drill‑down detail table includes: PO #, PO LINE, Supplier, Item, Material Category, REQUESTED DATE, CONFIRMED DATE, RECEIPT DATE, ORDERED QUANTITY, RECEIVED QUANTITY, TIMING STATUS, QUANTITY STATUS, VARIANCE %, OVERALL STATUS.
- Historical YTD comparison (2026 vs 2025) uses the archive tables (5109/5110) if available.

## Revision History
- **2026‑06‑03**: Updated to reflect the latest ControlTowerV9.html wireframe and client‑answered data‑questions (see Client_Data_Questions.docx). Removed references to OTD, IFD, PPV, lead‑time variance as separate KPIs; kept only Inbound PO Adherence %.