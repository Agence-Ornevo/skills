# Action Items Sheet Template - Standard KPI Column Structure

## Column Definitions (Level 1_2 Sheet)

| Column | Header | Purpose | Example |
|--------|--------|---------|---------|
| A | Dashboard | Dashboard name + slicers + layout (merged A:C) | "D02 — Service & Fulfillment\nSlicers: Period \| Country \| Product Category \| Channel\nLayout: 6 KPI cards..." |
| B | Slicers | (Merged into A for dashboard rows) | — |
| C | layout | (Merged into A for dashboard rows) | — |
| D | KPI ID and Name | KPI identifier + display name | "KPI-OTIF - OTIF" |
| E | Data sources from BC | Specific BC tables, fields, entities | "bc.SalesShipmentLine (shipmentDate, quantity), bc.SalesLineArchive (Promised_Delivery_Date)" |
| F | Data sources from Sharepoint | SharePoint files, lists, or external sources | "ENT-217 Customer Sales SharePoint (for Channel slicer)" |
| G | Action Item / questions | Client questions, blockers, email items | "Q6/Q7: On-Time tolerance (0/10/14 days)? Promised date field? \| EMAIL ITEM 4: Archive tables as OData" |
| H | KP-Answer | Proposed answer, fallback, confirmation needed | "Proposed: 0d standard / 10d regional / 14d long-haul. Promised_Delivery_Date on Sales Line." |
| I | Status | Current state | "Pending client confirmation on tolerance; Archive tables access needed" |

## Row Structure

1. **Dashboard Summary Row** (1 per dashboard, 8 total)
   - Columns A-C: Merged, contains dashboard name, slicers, layout
   - Column D: Empty
   - Columns E-I: Empty (or high-level notes)

2. **KPI Detail Rows** (1 per KPI, 42 total)
   - Columns A-C: Empty (visual indentation)
   - Column D: KPI ID and Name
   - Columns E-I: Populated with 5 detail fields

## Standard KPI IDs (Kings Pastry)

| Dashboard | KPI IDs |
|-----------|---------|
| D01 | KPI-OTIF, KPI-DOH-FG, KPI-INBOUND-PO, KPI-SCCOST |
| D02 | KPI-OTIF, KPI-ONTIMESHIP, KPI-FILLRATE, KPI-STOCKOUT-FG, KPI-STOCKOUT-ING, KPI-REQPROMADH |
| D03 | KPI-DOH-FG, KPI-DOH-ING, KPI-DOH-PKG, KPI-INVACC, KPI-AGINGFG, KPI-AGINGRAW, KPI-SLOWMOV, KPI-BELOWSS |
| D04 | KPI-THROUGHPUT, KPI-SCHEDADH, KPI-MATAVAIL, KPI-LABOUR |
| D05 | KPI-INBOUND-PO, KPI-LEADTIME, KPI-PPV, KPI-SPENDEXP |
| D06 | KPI-SCCOST, KPI-OUTFREIGHT, KPI-STORAGE, KPI-LABOURCOST |
| D07 | KPI-LABOUR, KPI-PICKACC, KPI-CAPUTIL, KPI-INVINTFG, KPI-INVINTPKG, KPI-INVINTRAW |
| D08 | KPI-OPENALERTS, KPI-AGEDALERTS, KPI-HVRISK, KPI-STOCKOUTRISK, KPI-SERVICERISK, KPI-COSTLEAK |

## Formatting Standards

- Header row (1): Dark blue (#4472C4), white bold, centered, wrapped
- Dashboard rows: Light blue (#D9E2F3), bold, merged A:C
- KPI rows: Indent col D (1 level), light gray (#F2F2F2) on cols A-C
- All cells: Thin borders
- Frozen panes: A2
- Auto-filter: A1:I{last_row}
- Column widths: A=35, B=25, C=25, D=45, E=30, F=30, G=40, H=15, I=15

## Usage

Copy this structure when creating new action item sheets for multi-dashboard BI projects.