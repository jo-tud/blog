#!/usr/bin/env python3
"""Generate the default link-preview card (static/og-card.png, 1200x630).

Used by LinkedIn, Mastodon & co. for the home page, pages and posts without an image.
Run once after changing the title or design; the PNG is committed.
"""

import hashlib
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "static" / "fonts"
OUT = ROOT / "static" / "og-card.png"

W, H = 1200, 630
BG, FG, FG_DIM, FG_FAINT = "#e9e9e4", "#1b1b19", "#56564f", "#85857d"
DOT, BLUE = "#c4c4bb", "#002fa7"

TITLE = os.environ.get("SITE_TITLE", "Sparse Rewards")
SUBTITLE = os.environ.get(
    "SITE_SUBTITLE", "Occasional notes on AI, learning, science, and the strange shape of progress.")
DOMAIN = "sparserewards.de"


def reward(seed, cols, rows):
    """Same rule as sparse_strip() in build.py: never the middle row or the middle third."""
    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16)
    candidates = [
        i for i in range(cols * rows)
        if not (rows % 2 and i // cols == rows // 2)
        and not (cols / 3 <= i % cols < 2 * cols / 3)
    ]
    return candidates[h % len(candidates)]


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


def main():
    scale = 2  # draw at double size, then downsample for smooth dots and text
    img = Image.new("RGB", (W * scale, H * scale), BG)
    d = ImageDraw.Draw(img)
    s = lambda v: int(v * scale)
    margin = 96

    # Dot field across the top, like the motif under each post title
    cols, rows, gap, r = 40, 3, 26.4, 3.0
    hit = reward(TITLE, cols, rows)
    for i in range(cols * rows):
        x = margin + (i % cols) * gap
        y = 120 + (i // cols) * gap
        rad, fill = (r * 2.4, BLUE) if i == hit else (r, DOT)
        d.ellipse([s(x - rad), s(y - rad), s(x + rad), s(y + rad)], fill=fill)

    title_font = ImageFont.truetype(str(FONTS / "IBMPlexSans-SemiBold.ttf"), s(84))
    sub_font = ImageFont.truetype(str(FONTS / "IBMPlexSans-Regular.ttf"), s(38))
    mono_font = ImageFont.truetype(str(FONTS / "IBMPlexMono-Regular.ttf"), s(26))

    d.text((s(margin), s(250)), TITLE, font=title_font, fill=FG)
    y = 372
    for line in wrap(d, SUBTITLE, sub_font, s(W - 2 * margin)):
        d.text((s(margin), s(y)), line, font=sub_font, fill=FG_DIM)
        y += 54
    d.text((s(margin), s(H - 96)), DOMAIN, font=mono_font, fill=FG_FAINT)

    img.resize((W, H), Image.LANCZOS).save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
