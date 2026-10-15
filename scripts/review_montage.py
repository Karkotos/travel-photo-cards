# -*- coding: utf-8 -*-
"""Grid montage of rendered card PNGs for quick visual QA.

Usage: python review_montage.py <png_dir> [out.jpg] [cols]
"""
import os
import sys

from PIL import Image, ImageDraw

from fontpick import pick

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SRC, "montage.jpg")
COLS = int(sys.argv[3]) if len(sys.argv) > 3 else 4

files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".png"))
if not files:
    sys.exit("no png in " + SRC)
TH_W = 300
font = pick(22, bold=True)

thumbs = []
for f in files:
    im = Image.open(os.path.join(SRC, f)).convert("RGB")
    h = int(TH_W * im.size[1] / im.size[0])
    im = im.resize((TH_W, h), Image.LANCZOS)
    thumbs.append((f, im))

TH_H = max(t.size[1] for _, t in thumbs)
rows = (len(thumbs) + COLS - 1) // COLS
GAP, TAG = 10, 34
sheet = Image.new("RGB", (COLS * (TH_W + GAP) + GAP, rows * (TH_H + TAG + GAP) + GAP), "#222")
d = ImageDraw.Draw(sheet)
for i, (f, t) in enumerate(thumbs):
    r, c = divmod(i, COLS)
    x, y = GAP + c * (TH_W + GAP), GAP + r * (TH_H + TAG + GAP)
    sheet.paste(t, (x, y))
    d.text((x + 4, y + TH_H + 4), "%02d %s" % (i + 1, f[:26]), font=font, fill="yellow")
sheet.save(OUT, quality=88)
print("montage:", OUT, sheet.size)
