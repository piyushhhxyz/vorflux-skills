---
name: pdf-2
description: This skill should be used when the user asks to create a PDF, generate a PDF report, export something as PDF, convert Markdown or HTML to PDF, build a PDF document, create an invoice PDF, or produce a printable report. Invoke with /pdf-2. Trigger phrases include "create a PDF", "generate a PDF report", "export as PDF", "convert to PDF", "make a PDF", "build a PDF document", "create an invoice PDF".
version: 1.0.0
user-invocable: true
argument-hint: [filename, template-name, or topic]
allowed-tools: Read, Write, Bash
---

# PDF-2 — Professional PDF Document Generator

Generate polished `.pdf` documents — reports, invoices, READMEs, letters — using HTML+CSS templates and WeasyPrint.

## How to use

```
/pdf-2 [filename, template-name, or topic]
```

## Available templates (in `templates/`)

| Template     | Description                                    |
|--------------|------------------------------------------------|
| `report`     | Multi-section technical/business report        |
| `invoice`    | Professional client invoice with line items    |
| `letter`     | Formal business letter                         |
| `readme`     | Formatted README/documentation export          |

## Instructions

### Step 1 — Determine source

- If `$ARGUMENTS` is a `.md` file → read and convert to PDF using the `readme` template
- If `$ARGUMENTS` matches a template name → load `templates/<name>.html` and fill it
- Otherwise → treat as topic, generate content, pick best template

### Step 2 — Build content dict

Gather all fields needed for the template (title, sections, tables, date, etc.) and save as `/tmp/pdf_data.json`.

### Step 3 — Render via script

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/generate_pdf.py /tmp/pdf_data.json output.pdf
```

The script fills the Jinja2 HTML template and renders via WeasyPrint.

### Step 4 — Report

Tell the user the output filename. Offer to adjust styling, add a TOC, or export as HTML.
