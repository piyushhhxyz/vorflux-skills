---
name: xlsx
description: This skill should be used when the user asks to create an Excel spreadsheet, generate an XLSX file, make a spreadsheet, build a data table in Excel, create a workbook, export data to Excel, add formulas to a sheet, or create a budget/tracker/report in Excel. Trigger phrases include "create an Excel file", "make a spreadsheet", "generate XLSX", "export to Excel", "build a workbook", "create a budget spreadsheet", "make a tracker".
version: 1.0.0
user-invocable: true
argument-hint: [template-name or data-file]
allowed-tools: Read, Write, Bash
---

# XLSX — Excel Workbook Generator

Generate professional `.xlsx` workbooks with formulas, charts, conditional formatting, and multiple sheets using the bundled generator script and named templates.

## How to use

```
/xlsx [template-name or data-file]
```

## Available templates (in `templates/`)

| Template          | Description                              |
|-------------------|------------------------------------------|
| `budget`          | Monthly budget tracker with categories  |
| `project-tracker` | Task/milestone tracker with status       |
| `invoice`         | Client invoice with auto-totals          |
| `kpi-dashboard`   | KPI metrics dashboard with charts        |
| `data-import`     | Generic CSV → formatted table importer   |

## Instructions

### Step 1 — Determine the source

- If `$ARGUMENTS` matches a template name above → load `templates/<name>.json` for schema
- If `$ARGUMENTS` is a `.csv` or `.json` file → read and use as data
- Otherwise → gather requirements and pick the closest template

### Step 2 — Prepare the data JSON

Build a data structure and save to `/tmp/xlsx_data.json`:

```json
{
  "filename": "output.xlsx",
  "template": "budget",
  "sheets": [
    {
      "name": "Summary",
      "headers": ["Category", "Budget", "Actual", "Variance", "Status"],
      "rows": [["Marketing", 5000, 4200, "=C2-B2", "=IF(D2>=0,\"Under\",\"Over\")"]],
      "totals_row": true,
      "chart": { "type": "bar", "title": "Budget vs Actual", "x_col": 0, "y_cols": [1, 2] }
    }
  ],
  "freeze_header": true,
  "auto_filter": true
}
```

### Step 3 — Run the generator

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/generate_xlsx.py /tmp/xlsx_data.json
```

### Step 4 — Report output

Tell the user filename, sheet names, and any formulas added. Offer to add charts or pivot summaries.
