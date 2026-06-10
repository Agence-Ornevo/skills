---
name: dashboard-action-items-architecture
description: Design and maintain the Level 1_2 sheet of Dashboard_action_Items.xlsx for multi‑dashboard KPI tracking.
trigger: "User requests a layout for the Action Items Excel sheet or needs to add KPI columns with a two‑level header."
---

## Overview
This skill defines the standard workflow for constructing the **Level 1_2** sheet in `Action_items/Dashboard_action_Items.xlsx`. The sheet must present each dashboard (D01‑D08) with slicer/configuration columns and a repeatable KPI block containing:
- **Data sources from BC**
- **Data sources from Sharepoint**
- **Action Item / questions**
- **KP‑Answer**
- **Status**

A two‑level header is used: the top level holds the dashboard name, slicers and layout; the second level groups the five KPI‑specific columns under each KPI ID/Name.

## Step‑by‑step process
1. **Load workbook** – Use `pandas.read_excel` with `header=1` (skip the empty first row) to read the existing *Level 1_2* sheet.
2. **Parse KPI listings** – Split the multiline KPI string, extract KPI IDs (text before the first ` - `), and map each KPI to its dashboard.
3. **Define column hierarchy** – Use a flat column layout (not MultiIndex) with: `Dashboard`, `Slicers`, `layout`, `KPI ID and Name`, then the five KPI sub‑fields (`Data sources from BC`, `Data sources from Sharepoint`, `Action Item / questions`, `KP‑Answer`, `Status`). This is simpler and works better with merged dashboard rows.
4. **Create empty DataFrame** – Populate rows for the eight dashboards (one summary row each), then add KPI detail rows under each dashboard (Dashboard/Slicers/layout blank for indentation). Write to a new sheet `Level 1_2_mod` using `pandas.ExcelWriter` with `engine='openpyxl'` and `mode='a'`.
5. **Apply formatting with openpyxl** – Load the workbook with `openpyxl`, then:
   - Unmerge dashboard rows (A:C), write combined dashboard name + slicers + layout into A, re-merge A:C
   - Apply header styling (dark blue background, white bold text, centered)
   - Apply dashboard row styling (light blue background, bold)
   - Apply KPI row styling (indent KPI name, light gray on cols A‑C)
   - Add thin borders to all cells
   - Set column widths per column
   - Freeze panes at `A2`
   - Enable auto-filter on `A1:I{last_row}`
6. **Populate KPI content from source documents** – Extract data from:
   - Dashboard-specific folders (e.g., `D02_Service_Fulfillment/`)
   - `Client_Data_Questions.docx` (use `python-docx`)
   - EML email files (read as text, parse for action items)
   - Map each question/answer to the relevant KPI rows
7. **Handle cross-cutting items** – Email items that apply to multiple KPIs across dashboards (e.g., Archive tables OData endpoints, tolerance windows) should be appended to each affected KPI's Action Items column.
8. **Validate** – Re‑read the sheet and verify all 5 detail columns are populated for every KPI row.

## Pitfalls & Mitigations
- **Missing KPI delimiter** – Some KPI rows may lack the ` - ` separator. Fallback: treat the whole line as the KPI ID.
- **Duplicate KPI IDs across dashboards** – Ensure the flat column layout uses exact KPI ID strings; duplicates are allowed because they appear under separate dashboard rows.
- **Merged cells are read-only** – In openpyxl, cells that are part of a merged range cannot have their `.value` set directly. Must `unmerge_cells()`, write to the top-left cell, then `merge_cells()` again and re-apply formatting.
- **Preserving styles** – `openpyxl` will keep basic cell styling; complex formatting (merged cells, colors) must be reapplied manually after writing data.
- **Overwriting the original sheet** – The workflow writes to a *new* sheet (`Level 1_2_mod`) to avoid accidental data loss. Once verified, copy formatting to the original sheet name.
- **python-docx not installed by default** – Need `pip install python-docx` in the execution environment before reading `.docx` files.
- **EML files are plain text** – `.eml` files can be read directly with `read_file`; they contain both plain text and HTML parts (base64 encoded). Parse the plain text part for action items.
- **Cross-cutting email items** – Items from emails (e.g., archive table endpoints, tolerance windows) often apply to multiple KPIs across dashboards. Append to each affected KPI's Action Items column rather than duplicating rows.

## Reference files
- `references/dashboard_action_items_session.md` – detailed session transcript and example output.

## Future extensions
- Auto‑populate slicer values by parsing `Dashboard_Hierarchy_Diagram.html`.
- Add a script (`scripts/generate_action_items_excel.py`) that can be run independently to regenerate the sheet from source KPI spec files.
