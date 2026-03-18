---
name: pptx
description: This skill should be used when the user asks to create a PowerPoint presentation, make slides, generate a PPTX file, build a slide deck, or export content as a presentation. Trigger phrases include "create a presentation", "make slides", "generate PPTX", "build a slide deck", "make a PowerPoint", "turn this into slides", "create a slideshow".
version: 1.0.0
user-invocable: true
argument-hint: [topic or filename]
allowed-tools: Read, Write, Bash
---

# PPTX — PowerPoint Presentation Generator

Generate professional `.pptx` files using the bundled Python script and theme templates.

## How to use

```
/pptx [topic or filename]
```

## Instructions

### Step 1 — Collect input

If `$ARGUMENTS` is a `.md` or `.txt` file, read it for content. Otherwise use it as a topic/title.

Ask (or infer):
- Slide count (default 8–12)
- Audience (technical, executive, general)
- Theme: `corporate`, `dark`, `minimal` (see `templates/themes.json`)

### Step 2 — Build the slide manifest

Create a JSON manifest with this shape and save it as `/tmp/pptx_manifest.json`:

```json
{
  "title": "...",
  "theme": "corporate",
  "author": "...",
  "slides": [
    { "layout": "title",   "title": "...", "subtitle": "..." },
    { "layout": "content", "title": "...", "bullets": ["...", "..."] },
    { "layout": "two_col", "title": "...", "left": ["..."], "right": ["..."] },
    { "layout": "image",   "title": "...", "caption": "..." },
    { "layout": "quote",   "quote": "...", "author": "..." },
    { "layout": "closing", "title": "Thank You", "subtitle": "..." }
  ]
}
```

### Step 3 — Run the generator

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/generate_pptx.py /tmp/pptx_manifest.json output.pptx
```

### Step 4 — Report

Tell the user the output filename and slide count. Offer theme changes or additional slides.

## Layout types

| Layout    | Use for                          |
|-----------|----------------------------------|
| `title`   | First and section-break slides   |
| `content` | Standard bullet-point slide      |
| `two_col` | Comparisons, pros/cons           |
| `image`   | Visual/diagram placeholder       |
| `quote`   | Testimonials, impactful stats    |
| `closing` | Final thank-you / CTA slide      |
