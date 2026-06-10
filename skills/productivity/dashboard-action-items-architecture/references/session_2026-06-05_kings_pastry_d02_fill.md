# Session Reference: Kings Pastry D02–D08 Action Items Fill (2026-06-05)

## Context
Filled all 8 dashboards (D01–D08) and 42 KPIs in `Action_items/Dashboard_action_Items.xlsx` Level 1_2 sheet with:
- BC data sources (specific tables/fields)
- SharePoint data sources (ENT-217, ENT-203, ENT-204, ADP mapping)
- Action Items / Questions from Client_Data_Questions.docx + EML email
- KP Answers (proposed solutions, fallbacks, confirmations needed)
- Status (Blocked / Pending / Critical / Dependent)

## Source Documents Used
| Source | Location | Content |
|--------|----------|---------|
| D02 Docs | `D02_Service_Fulfillment/` | KPI Definitions, Data Source Map, Data Structure Analysis, Build Plan, DAX Measures, Validation |
| Client Questions | `Client_Data_Questions.docx` | 43 questions (Q1–Q43) across L1 Global, Slicers, L2 Dashboard-level |
| Email | `Action_items/Action Required_ Data & Questions Blocking D07 Testing...eml` | 9 items blocking D07 testing + historical KPIs |

## Key Patterns

### 1. Flat Column Layout (not MultiIndex)
```python
target_cols = ['Dashboard', 'Slicers', 'layout', 'KPI ID and Name',
               'Data sources from BC', 'Data sources from Sharepoint',
               'Action Item / questions', 'KP-Answer', 'Status']
```

### 2. Merged Dashboard Row Pattern
```python
ws.unmerge_cells(f'A{row_idx}:C{row_idx}')
dash_text = f"{dash_name}\nSlicers: {slicers_text}\nLayout: {layout_text}"
ws.cell(row=row_idx, column=1, value=dash_text)
ws.merge_cells(f'A{row_idx}:C{row_idx}')
# Re-apply formatting to merged cell
```

### 3. KPI Row Population
```python
ws.cell(row=row_idx, column=5, value=bc_src)      # BC sources
ws.cell(row=row_idx, column=6, value=sp_src)      # SharePoint sources
ws.cell(row=row_idx, column=7, value=action_items) # Questions
ws.cell(row=row_idx, column=8, value=kp_answer)    # Answers
ws.cell(row=row_idx, column=9, value=status)       # Status
```

### 4. Cross-Cutting Email Items
```python
# Append to existing Action Items column
cell = ws.cell(row=kpi_row, column=7)
cell.value = (cell.value or "") + f"\nEMAIL ITEM N: {description}"
```

### 5. Document Parsing
```python
# Word doc
import docx
doc = docx.Document(path)
for para in doc.paragraphs:
    if para.text.strip():
        print(para.text)

# EML file - read as text, plain text part is base64 decoded
# Or just read the raw file and extract plain text section
```

## Blocker Summary
| Blocker | Affected Dashboards | Resolution |
|---------|---------------------|------------|
| ENT-T07 ADP→BC mapping (19/31 codes) | D04, D07 Labour | Fill SharePoint mapping file |
| SalesHeaderArchive (5107) + SalesLineArchive (5108) OData | D01, D02, D07 historical | Enable as OData endpoints |
| ENT-215 Demand Forecast | D01, D03 DOH | Client to provide forecast file |
| ENT-203 Freight file | D01, D06 | Logistics team to provide |
| ENT-204 Standard Cost | D05 PPV | Finance to provide |
| GL Mapping (ENT-T05) | D01, D06 cost KPIs | Finance to map GL accounts |
| On-Time tolerance (0/10/14d) | D01, D02 | CS+Ops to confirm by lane |

## Dashboard-KPI Map
- D01: OTIF, DOH-FG, Inbound-PO, SCCOST (4)
- D02: OTIF, OnTimeShip, FillRate, Stockout-FG, Stockout-ING, ReqPromAdh (6)
- D03: DOH-FG/ING/PKG, InvAcc, Aging-FG/RAW, SlowMov, BelowSS (8)
- D04: Throughput, SchedAdh, MatAvail, Labour (4)
- D05: Inbound-PO, LeadTime, PPV, SpendExp (4)
- D06: SCCOST, OutFreight, Storage, LabourCost (4)
- D07: Labour, PickAcc, CapUtil, InvInt-FG/PKG/RAW (6)
- D08: OpenAlerts, AgedAlerts, HVRisk, StockoutRisk, ServiceRisk, CostLeak (6)
**Total: 42 KPIs**