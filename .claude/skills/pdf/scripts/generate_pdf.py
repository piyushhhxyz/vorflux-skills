#!/usr/bin/env python3
"""
PDF Generator — Claude Code Skill
Usage: python3 generate_pdf.py <data.json> <output.pdf>
Requires: pip install weasyprint jinja2 markdown
"""

import json
import sys
import os
from pathlib import Path
from datetime import date

# Install dependencies silently
def ensure_deps():
    deps = {"weasyprint": "weasyprint", "jinja2": "Jinja2", "markdown": "markdown"}
    for module, package in deps.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {package}...")
            os.system(f"pip install {package} -q")

ensure_deps()

import markdown as md_lib
from jinja2 import Environment, FileSystemLoader, BaseLoader
import weasyprint

SKILL_DIR = Path(__file__).parent.parent

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.65;
  color: #222;
  background: #fff;
}

/* ── Page layout ── */
@page {
  size: A4;
  margin: 22mm 20mm 25mm 20mm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-size: 8pt;
    color: #888;
  }
}

/* ── Header bar ── */
.doc-header {
  border-bottom: 3px solid #005AA7;
  padding-bottom: 10px;
  margin-bottom: 28px;
}
.doc-header h1 { font-size: 22pt; color: #005AA7; font-weight: 700; }
.doc-header .meta { font-size: 9pt; color: #666; margin-top: 4px; }

/* ── Headings ── */
h1 { font-size: 18pt; color: #005AA7; margin: 24px 0 10px; }
h2 { font-size: 13pt; color: #1A3A5C; margin: 20px 0 8px; border-bottom: 1px solid #dce8f5; padding-bottom: 4px; }
h3 { font-size: 11pt; color: #2C5F8A; margin: 14px 0 6px; }

/* ── Body text ── */
p  { margin-bottom: 10px; }
ul, ol { margin: 8px 0 10px 22px; }
li { margin-bottom: 4px; }

/* ── Tables ── */
table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 9.5pt; }
thead tr { background: #005AA7; color: #fff; }
thead th { padding: 8px 10px; text-align: left; font-weight: 600; }
tbody tr:nth-child(even) { background: #EBF4FB; }
tbody td { padding: 7px 10px; border-bottom: 1px solid #d0dce8; }
tfoot td { font-weight: 700; background: #D6E8F7; padding: 8px 10px; }

/* ── Code ── */
code { font-family: 'Courier New', monospace; font-size: 9pt; background: #f4f6f8; padding: 1px 5px; border-radius: 3px; }
pre  { background: #f4f6f8; border-left: 4px solid #005AA7; padding: 12px 14px; margin: 12px 0; overflow-x: auto; }
pre code { background: none; padding: 0; }

/* ── Invoice specific ── */
.invoice-meta { display: flex; justify-content: space-between; margin-bottom: 28px; }
.invoice-meta .block h3 { color: #444; font-size: 9pt; text-transform: uppercase; letter-spacing: 0.05em; }
.invoice-meta .block p  { font-size: 10pt; color: #222; }
.invoice-total { text-align: right; margin-top: 12px; }
.invoice-total .total-line { font-size: 14pt; font-weight: 700; color: #005AA7; }

/* ── Alert boxes ── */
.callout { border-left: 4px solid; padding: 10px 14px; margin: 14px 0; border-radius: 0 4px 4px 0; }
.callout.info    { border-color: #005AA7; background: #EBF4FB; }
.callout.warning { border-color: #E67E22; background: #FEF5EC; }
.callout.success { border-color: #27AE60; background: #EAFAF1; }

/* ── Page break ── */
.page-break { page-break-after: always; }
"""

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><style>{{ css }}</style></head>
<body>
  <div class="doc-header">
    <h1>{{ title }}</h1>
    <div class="meta">{{ subtitle }} &nbsp;|&nbsp; {{ date }} &nbsp;|&nbsp; {{ author }}</div>
  </div>

  {% for section in sections %}
  <h2>{{ section.heading }}</h2>
  {% if section.get('intro') %}<p>{{ section.intro }}</p>{% endif %}

  {% if section.get('bullets') %}
  <ul>{% for b in section.bullets %}<li>{{ b }}</li>{% endfor %}</ul>
  {% endif %}

  {% if section.get('table') %}
  <table>
    <thead><tr>{% for h in section.table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
    <tbody>
    {% for row in section.table.rows %}
    <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
    {% endfor %}
    </tbody>
    {% if section.table.get('footer') %}
    <tfoot><tr>{% for cell in section.table.footer %}<td>{{ cell }}</td>{% endfor %}</tr></tfoot>
    {% endif %}
  </table>
  {% endif %}

  {% if section.get('callout') %}
  <div class="callout {{ section.callout.type }}"><strong>{{ section.callout.title }}:</strong> {{ section.callout.text }}</div>
  {% endif %}

  {% if section.get('markdown') %}{{ section.markdown | markdown }}{% endif %}
  {% endfor %}
</body>
</html>"""

INVOICE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><style>{{ css }}</style></head>
<body>
  <div class="doc-header">
    <h1>INVOICE</h1>
    <div class="meta">Invoice #{{ invoice_number }} &nbsp;|&nbsp; Date: {{ date }} &nbsp;|&nbsp; Due: {{ due_date }}</div>
  </div>

  <div class="invoice-meta">
    <div class="block">
      <h3>From</h3>
      <p><strong>{{ from.name }}</strong><br>{{ from.address }}<br>{{ from.email }}</p>
    </div>
    <div class="block">
      <h3>Bill To</h3>
      <p><strong>{{ to.name }}</strong><br>{{ to.address }}<br>{{ to.email }}</p>
    </div>
  </div>

  <table>
    <thead><tr><th>#</th><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>
    <tbody>
    {% for item in items %}
    <tr>
      <td>{{ loop.index }}</td>
      <td>{{ item.description }}</td>
      <td>{{ item.qty }}</td>
      <td>${{ "%.2f"|format(item.unit_price) }}</td>
      <td>${{ "%.2f"|format(item.qty * item.unit_price) }}</td>
    </tr>
    {% endfor %}
    </tbody>
    <tfoot>
      <tr><td colspan="4" style="text-align:right">Subtotal</td><td>${{ "%.2f"|format(subtotal) }}</td></tr>
      {% if tax_rate %}<tr><td colspan="4" style="text-align:right">Tax ({{ tax_rate }}%)</td><td>${{ "%.2f"|format(subtotal * tax_rate / 100) }}</td></tr>{% endif %}
      <tr><td colspan="4" style="text-align:right"><strong>TOTAL</strong></td><td><strong>${{ "%.2f"|format(total) }}</strong></td></tr>
    </tfoot>
  </table>

  {% if notes %}<p style="color:#666;font-size:9pt;margin-top:20px"><strong>Notes:</strong> {{ notes }}</p>{% endif %}
</body>
</html>"""

README_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><style>{{ css }}</style></head>
<body>
  <div class="doc-header">
    <h1>{{ title }}</h1>
    <div class="meta">Generated {{ date }}</div>
  </div>
  {{ content | safe }}
</body>
</html>"""


def markdown_filter(text):
    return md_lib.markdown(text, extensions=["tables", "fenced_code", "toc"])


def render_report(data: dict) -> str:
    env = Environment(loader=BaseLoader())
    env.filters["markdown"] = markdown_filter
    tmpl = env.from_string(REPORT_TEMPLATE)
    return tmpl.render(css=CSS, date=date.today().strftime("%B %d, %Y"), **data)


def render_invoice(data: dict) -> str:
    items    = data.get("items", [])
    subtotal = sum(i["qty"] * i["unit_price"] for i in items)
    tax_rate = data.get("tax_rate", 0)
    total    = subtotal + subtotal * tax_rate / 100
    env  = Environment(loader=BaseLoader())
    tmpl = env.from_string(INVOICE_TEMPLATE)
    return tmpl.render(css=CSS, date=date.today().strftime("%B %d, %Y"),
                       subtotal=subtotal, total=total, **data)


def render_readme(data: dict) -> str:
    raw     = data.get("markdown", "")
    content = md_lib.markdown(raw, extensions=["tables", "fenced_code", "toc"])
    env  = Environment(loader=BaseLoader())
    tmpl = env.from_string(README_TEMPLATE)
    return tmpl.render(css=CSS, date=date.today().strftime("%B %d, %Y"),
                       content=content, **data)


RENDERERS = {
    "report":  render_report,
    "invoice": render_invoice,
    "readme":  render_readme,
}


def generate(data_path: str, output_path: str):
    with open(data_path) as f:
        data = json.load(f)

    template = data.get("template", "report")
    renderer = RENDERERS.get(template, render_report)
    html     = renderer(data)

    weasyprint.HTML(string=html).write_pdf(output_path)
    print(f"✅  Saved PDF → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_pdf.py <data.json> <output.pdf>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
