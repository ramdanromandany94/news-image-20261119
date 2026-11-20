#!/usr/bin/env python3
"""Render the 19 November 2026 world-news front page as a 1024x1024 PNG.

Everything is drawn with PIL primitives and the DejaVu fonts that ship with
the system: no network, no generated imagery, no timestamps in the file, so
two runs write byte-identical output. Run it from the repository root:

    python3 tools/render.py

It writes entry.png next to the repository root (the file main.ts copies to
/output/entry.png). Layout: a newspaper front page — masthead with the date
in large type, one hero panel for the Shenzhen three-way meeting, a 2x2 grid
for the other four big stories, a wide strip for the Anthropic IPO, and an
"ALSO TODAY" strip for five smaller stories.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (163, 22, 22)
MUTED = (96, 92, 84)
RULE = (180, 172, 158)
PANEL_BG = (252, 250, 245)
STRIP_BG = (233, 236, 240)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    """Load a DejaVu font, falling back to PIL's built-in bitmap font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: load("DejaVuSerif-Bold.ttf", s)   # masthead, hero headline
SANS_B = lambda s: load("DejaVuSans-Bold.ttf", s)     # kickers, titles
SANS = lambda s: load("DejaVuSans.ttf", s)            # body text


def wrap(draw, text, font, max_w):
    """Split text into lines that fit max_w pixels, word by word."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, x, y, text, font, max_w, fill=INK, leading=1.25):
    """Draw wrapped text; returns the y just below the last line."""
    line_h = int(font.size * leading)
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def star_points(cx, cy, r_out, r_in, rot=-90):
    """Vertices of a five-pointed star, for the Chinese flag."""
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def flag_usa(draw, x, y, w, h):
    """Simplified Stars and Stripes: red/white bands, blue canton, dot stars."""
    draw.rectangle([x, y, x + w, y + h], fill=WHITE)
    stripe = h / 13
    for i in range(0, 13, 2):
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                       fill=(178, 34, 52))
    canton_w, canton_h = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + canton_w, y + canton_h], fill=(60, 59, 110))
    for row in range(3):
        for col in range(4):
            cx = x + 6 + col * (canton_w - 10) / 3
            cy = y + 5 + row * (canton_h - 9) / 2
            draw.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5], fill=WHITE)


def flag_china(draw, x, y, w, h):
    """Simplified Chinese flag: red field, one big yellow star, four small."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    draw.polygon(star_points(x + w * 0.22, y + h * 0.30, h * 0.22, h * 0.09),
                 fill=(255, 222, 0))
    for dx, dy in [(0.52, 0.12), (0.64, 0.24), (0.64, 0.42), (0.52, 0.54)]:
        draw.polygon(star_points(x + w * dx, y + h * dy, h * 0.08, h * 0.033),
                     fill=(255, 222, 0))


def flag_russia(draw, x, y, w, h):
    """Russian tricolour: white, blue, red horizontal bands."""
    third = h / 3
    draw.rectangle([x, y, x + w, y + third], fill=WHITE)
    draw.rectangle([x, y + third, x + w, y + 2 * third], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * third, x + w, y + h], fill=(213, 0, 50))


def kicker(draw, x, y, text, size=16):
    """A red kicker label with a small square bullet; returns y below it."""
    draw.rectangle([x, y + 2, x + 10, y + 12], fill=RED)
    draw.text((x + 16, y), text, font=SANS_B(size), fill=RED)
    return y + size + 6


def grid_panel(draw, x, y, w, h, kick, title, body):
    """One 2-column grid panel: kicker, bold title (<=2 lines), body (<=3)."""
    draw.rectangle([x, y, x + w, y + h], fill=PANEL_BG, outline=RULE, width=1)
    px, py = x + 16, y + 12
    py = kicker(draw, px, py, kick, size=15)
    py = draw_wrapped(draw, px, py + 2, title, SANS_B(21), w - 32,
                      leading=1.12)
    draw_wrapped(draw, px, py + 6, body, SANS(15), w - 32, leading=1.25)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    title = "THE WORLD IN ONE IMAGE"
    f_title = SERIF_B(52)
    d.text(((W - d.textlength(title, font=f_title)) / 2, 24),
           title, font=f_title, fill=INK)
    d.rectangle([MARGIN, 96, W - MARGIN, 100], fill=RED)
    date = "THURSDAY 19 NOVEMBER 2026"
    f_date = SANS_B(34)
    d.text(((W - d.textlength(date, font=f_date)) / 2, 110),
           date, font=f_date, fill=RED)
    d.rectangle([MARGIN, 152, W - MARGIN, 154], fill=INK)

    # ---- Hero: Shenzhen three-way meeting -------------------------------
    hy = 168
    d.text((MARGIN, hy), "SHENZHEN  ·  APEC SUMMIT",
           font=SANS_B(19), fill=RED)
    headline = "TRUMP, XI & PUTIN MEET\nFOR THE FIRST TIME"
    d.multiline_text((MARGIN, hy + 30), headline, font=SERIF_B(40),
                     fill=INK, spacing=4)
    body = ("The three leaders meet on the sidelines of the APEC summit in "
            "Shenzhen — nuclear arms control, Ukraine, Iran and trade on the "
            "agenda. No major deal. China and Russia issue a 'peace "
            "declaration' that mentions neither Ukraine nor Iran.")
    draw_wrapped(d, MARGIN, hy + 128, body, SANS(20), 640, leading=1.3)

    # Three flags on the right of the hero panel.
    fx, fy, fw, fh = 700, hy + 118, 88, 56
    for i, (fn, label) in enumerate(
            [(flag_usa, "USA"), (flag_china, "CHINA"), (flag_russia, "RUSSIA")]):
        x = fx + i * (fw + 12)
        fn(d, x, fy, fw, fh)
        d.rectangle([x, fy, x + fw, fy + fh], outline=INK, width=1)
        lab = SANS_B(14)
        d.text((x + (fw - d.textlength(label, font=lab)) / 2, fy + fh + 6),
               label, font=lab, fill=MUTED)
    d.rectangle([MARGIN, 452, W - MARGIN, 454], fill=INK)

    # ---- Grid: the other four big stories -------------------------------
    gx, gy = MARGIN, 468
    cw, ch, gap = 466, 144, 20
    grid_panel(d, gx, gy, cw, ch,
               "THE HAGUE  ·  WORLD COURT",
               "MYANMAR GUILTY OF ROHINGYA GENOCIDE",
               "First genocide verdict against a state, 9–6. The 2017 "
               "campaign killed about 10,000 Rohingya.")
    grid_panel(d, gx + cw + gap, gy, cw, ch,
               "GAZA  ·  CEASEFIRE",
               "ISRAELI TANKS CROSS THE CEASEFIRE LINE",
               "Tanks push into central Gaza past the line near Nuseirat. "
               "Hamas calls it a breach; residents flee.")
    grid_panel(d, gx, gy + ch + 16, cw, ch,
               "UKRAINE  ·  CRIMEA",
               "KERCH BRIDGE STRUCK A THIRD TIME",
               "Ukraine hits the Crimea bridge again; rail traffic stops. "
               "Russian strikes kill ≥5 and cut power in five regions.")
    grid_panel(d, gx + cw + gap, gy + ch + 16, cw, ch,
               "THE GULF  ·  STRIKES",
               "U.S. HITS IRAN'S QESHM ISLAND",
               "Iran strikes back at Kuwait and Bahrain. A Houthi missile "
               "damages Riyadh's PIF Tower, the city's tallest building.")

    # ---- Wide strip: Anthropic IPO --------------------------------------
    ay = 788
    d.rectangle([MARGIN, ay, W - MARGIN, ay + 82], fill=PANEL_BG,
                outline=RULE, width=1)
    d.text((MARGIN + 16, ay + 8), "TECHNOLOGY", font=SANS_B(15), fill=RED)
    d.text((MARGIN + 16, ay + 28), "ANTHROPIC IPO SMASHES RECORDS",
           font=SANS_B(23), fill=INK)
    d.text((MARGIN + 16, ay + 56),
           "About $81 billion raised at $83 a share; trading begins today.",
           font=SANS(17), fill=MUTED)
    # Small ascending bar chart on the right of the strip.
    bx, by = W - MARGIN - 108, ay + 22
    for i, bh in enumerate([16, 26, 38]):
        x = bx + i * 30
        d.rectangle([x, by + 38 - bh, x + 20, by + 38], fill=RED)

    # ---- ALSO TODAY strip ------------------------------------------------
    ty = 882
    d.rectangle([MARGIN, ty, W - MARGIN, ty + 124], fill=STRIP_BG)
    d.text((MARGIN + 16, ty + 10), "ALSO TODAY", font=SANS_B(19), fill=INK)
    src = "SOURCES: AP · REUTERS · UN NEWS · JUST SECURITY"
    f_src = SANS_B(13)
    d.text((W - MARGIN - 16 - d.textlength(src, font=f_src), ty + 12),
           src, font=f_src, fill=MUTED)
    items_left = [
        "COP31 in final stretch: 'transition away' vs phaseout",
        "Bangladesh unrest: 4 dead, Yunus ancestral home burned",
        "LPG tanker Gas Husky sinks off Bulgaria after strike",
    ]
    items_right = [
        "Migrant boat sinks off Senegal: dozens missing, ~100 aboard",
        "IAEA: N. Korea expands uranium enrichment at Yongbyon",
    ]
    f_item = SANS(15)
    for i, item in enumerate(items_left):
        d.text((MARGIN + 16, ty + 44 + i * 26), "•  " + item,
               font=f_item, fill=INK)
    for i, item in enumerate(items_right):
        d.text((MARGIN + 492, ty + 44 + i * 26), "•  " + item,
               font=f_item, fill=INK)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "entry.png")
    img.save(out, format="PNG")
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    render()
