#!/usr/bin/env python3
"""
PPTX Generator — Claude Code Skill
Usage: python3 generate_pptx.py <manifest.json> <output.pptx>
Requires: pip install python-pptx
"""

import json
import sys
import os
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Inches, Pt
except ImportError:
    print("Installing python-pptx...")
    os.system("pip install python-pptx -q")
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

THEMES = {
    "corporate": {
        "bg":        RGBColor(0xFF, 0xFF, 0xFF),
        "accent":    RGBColor(0x00, 0x5A, 0xA7),
        "title_fg":  RGBColor(0x1A, 0x1A, 0x2E),
        "body_fg":   RGBColor(0x33, 0x33, 0x33),
        "bar_color": RGBColor(0x00, 0x5A, 0xA7),
    },
    "dark": {
        "bg":        RGBColor(0x1A, 0x1A, 0x2E),
        "accent":    RGBColor(0xE9, 0x4F, 0x37),
        "title_fg":  RGBColor(0xFF, 0xFF, 0xFF),
        "body_fg":   RGBColor(0xCC, 0xCC, 0xCC),
        "bar_color": RGBColor(0xE9, 0x4F, 0x37),
    },
    "minimal": {
        "bg":        RGBColor(0xFA, 0xFA, 0xFA),
        "accent":    RGBColor(0x2E, 0xCC, 0x71),
        "title_fg":  RGBColor(0x11, 0x11, 0x11),
        "body_fg":   RGBColor(0x44, 0x44, 0x44),
        "bar_color": RGBColor(0x2E, 0xCC, 0x71),
    },
}

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def set_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, text, left, top, width, height,
                font_size=18, bold=False, color=None, align=PP_ALIGN.LEFT, italic=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return txBox


def add_accent_bar(slide, theme, top=Inches(0.12)):
    bar = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(0), top, SLIDE_W, Inches(0.08)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = theme["bar_color"]
    bar.line.fill.background()


def build_title_slide(prs, slide_data, theme):
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)
    set_bg(slide, theme["bg"])
    # big accent block on left
    block = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(4.5), SLIDE_H)
    block.fill.solid()
    block.fill.fore_color.rgb = theme["accent"]
    block.line.fill.background()
    # title text
    add_textbox(slide, slide_data.get("title", "Title"),
                Inches(5), Inches(2.5), Inches(7.8), Inches(1.5),
                font_size=40, bold=True, color=theme["title_fg"], align=PP_ALIGN.LEFT)
    # subtitle
    add_textbox(slide, slide_data.get("subtitle", ""),
                Inches(5), Inches(4.2), Inches(7.8), Inches(1.2),
                font_size=22, color=theme["body_fg"], align=PP_ALIGN.LEFT)


def build_content_slide(prs, slide_data, theme):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    set_bg(slide, theme["bg"])
    add_accent_bar(slide, theme)
    add_textbox(slide, slide_data.get("title", ""),
                Inches(0.6), Inches(0.4), Inches(12), Inches(1.0),
                font_size=32, bold=True, color=theme["title_fg"])
    bullets = slide_data.get("bullets", [])
    body_top = Inches(1.6)
    for i, bullet in enumerate(bullets[:6]):
        add_textbox(slide, f"▸  {bullet}",
                    Inches(0.8), body_top + Inches(i * 0.78), Inches(11.5), Inches(0.7),
                    font_size=18, color=theme["body_fg"])


def build_two_col_slide(prs, slide_data, theme):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    set_bg(slide, theme["bg"])
    add_accent_bar(slide, theme)
    add_textbox(slide, slide_data.get("title", ""),
                Inches(0.6), Inches(0.4), Inches(12), Inches(1.0),
                font_size=32, bold=True, color=theme["title_fg"])
    # divider
    div = slide.shapes.add_shape(1, Inches(6.4), Inches(1.5), Inches(0.05), Inches(5.5))
    div.fill.solid()
    div.fill.fore_color.rgb = theme["accent"]
    div.line.fill.background()
    for i, item in enumerate(slide_data.get("left", [])[:5]):
        add_textbox(slide, f"• {item}",
                    Inches(0.6), Inches(1.7) + Inches(i * 0.72), Inches(5.5), Inches(0.65),
                    font_size=17, color=theme["body_fg"])
    for i, item in enumerate(slide_data.get("right", [])[:5]):
        add_textbox(slide, f"• {item}",
                    Inches(6.8), Inches(1.7) + Inches(i * 0.72), Inches(5.5), Inches(0.65),
                    font_size=17, color=theme["body_fg"])


def build_quote_slide(prs, slide_data, theme):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    set_bg(slide, theme["accent"])
    add_textbox(slide, "\u201C",
                Inches(0.5), Inches(0.3), Inches(2), Inches(2),
                font_size=120, color=RGBColor(0xFF, 0xFF, 0xFF))
    add_textbox(slide, slide_data.get("quote", ""),
                Inches(1.2), Inches(1.5), Inches(11), Inches(3.5),
                font_size=26, bold=False, italic=True,
                color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
    add_textbox(slide, f"\u2014 {slide_data.get('author', '')}",
                Inches(1.2), Inches(5.5), Inches(11), Inches(0.8),
                font_size=18, color=RGBColor(0xEE, 0xEE, 0xEE), align=PP_ALIGN.CENTER)


def build_closing_slide(prs, slide_data, theme):
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    set_bg(slide, theme["accent"])
    add_textbox(slide, slide_data.get("title", "Thank You"),
                Inches(1), Inches(2.4), Inches(11.3), Inches(1.5),
                font_size=54, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
    add_textbox(slide, slide_data.get("subtitle", ""),
                Inches(1), Inches(4.2), Inches(11.3), Inches(1),
                font_size=22, color=RGBColor(0xEE, 0xEE, 0xEE), align=PP_ALIGN.CENTER)


BUILDERS = {
    "title":   build_title_slide,
    "content": build_content_slide,
    "two_col": build_two_col_slide,
    "image":   build_content_slide,   # fallback to content
    "quote":   build_quote_slide,
    "closing": build_closing_slide,
}


def generate(manifest_path: str, output_path: str):
    with open(manifest_path) as f:
        manifest = json.load(f)

    theme_name = manifest.get("theme", "corporate")
    theme = THEMES.get(theme_name, THEMES["corporate"])

    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    for slide_data in manifest.get("slides", []):
        layout = slide_data.get("layout", "content")
        builder = BUILDERS.get(layout, build_content_slide)
        builder(prs, slide_data, theme)

    prs.save(output_path)
    print(f"✅  Saved {len(manifest['slides'])} slides → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_pptx.py <manifest.json> <output.pptx>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
