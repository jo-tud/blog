#!/usr/bin/env python3
"""Generate the favicon files from the dot motif. Run once after changing the design;
the output in static/ is committed, so the site build does not need Inkscape or ImageMagick.

The favicon is a 3x3 version of the logo: at 16 px the logo's 5x3 grid turns to mush.
Like everywhere else, the reward dot never sits in the middle row or column.
"""

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
SEED = "Sparse Rewards"
BG = "#e9e9e4"
DOT, DOT_DARK = "#9b9b93", "#8a8a83"
BLUE, BLUE_DARK = "#002fa7", "#6f8dff"


def reward_cell():
    h = int(hashlib.sha1(SEED.encode("utf-8")).hexdigest(), 16)
    corners = [0, 2, 6, 8]  # 3x3: everything off the middle row and column
    return corners[h % len(corners)]


def svg(background=None, adaptive=True):
    hit = reward_cell()
    circles = []
    for i in range(9):
        x, y = 6 + (i % 3) * 10, 6 + (i // 3) * 10
        if i == hit:
            circles.append(f'<circle class="hit" cx="{x}" cy="{y}" r="5"/>')
        else:
            circles.append(f'<circle cx="{x}" cy="{y}" r="2.6"/>')
    style = f"circle{{fill:{DOT}}}.hit{{fill:{BLUE}}}"
    if adaptive:
        style += f"@media (prefers-color-scheme:dark){{circle{{fill:{DOT_DARK}}}.hit{{fill:{BLUE_DARK}}}}}"
    bg = f'<rect width="32" height="32" fill="{background}"/>' if background else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            f'<style>{style}</style>{bg}{"".join(circles)}</svg>\n')


def render(svg_text, png_path, size):
    src = png_path.with_suffix(".tmp.svg")
    src.write_text(svg_text)
    subprocess.run(["inkscape", str(src), "--export-type=png", f"--export-filename={png_path}",
                    f"--export-width={size}", f"--export-height={size}"],
                   check=True, capture_output=True)
    src.unlink()


def main():
    (STATIC / "favicon.svg").write_text(svg())
    # Fallbacks for browsers without SVG favicons, and the iOS home screen (which wants a background)
    render(svg(adaptive=False), STATIC / "favicon-32.png", 32)
    render(svg(background=BG, adaptive=False), STATIC / "apple-touch-icon.png", 180)
    subprocess.run(["magick", str(STATIC / "favicon-32.png"), str(STATIC / "favicon.ico")], check=True)
    print("reward cell:", reward_cell())


if __name__ == "__main__":
    main()
