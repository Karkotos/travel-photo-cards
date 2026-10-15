# -*- coding: utf-8 -*-
"""Labeled contact sheets: review a photo folder quickly before selecting.

Usage: python contact_sheet.py <photo_dir> [outdir]
Outputs numbered sheets (yellow tag = file index) for visual selection.
"""
import os
import sys

from PIL import Image, ImageDraw

from fontpick import pick

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "select"
os.makedirs(OUT, exist_ok=True)
FONT = pick(26, bold=True)

files = []
for root, _, fs in os.walk(BASE):
    for f in sorted(fs):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            files.append(os.path.join(root, f))
files.sort()
print("total:", len(files))

TH_W, TH_H, COLS, PER = 360, 270, 5, 20
for si in range(0, len(files), PER):
    batch = files[si:si + PER]
    rows = (len(batch) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * (TH_W + 10) + 10, rows * (TH_H + 44) + 10), "#222")
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(batch):
        r, c = divmod(i, COLS)
        x, y = 10 + c * (TH_W + 10), 10 + r * (TH_H + 44)
        try:
            im = Image.open(f).convert("RGB")
            im.thumbnail((TH_W, TH_H))
            sheet.paste(im, (x, y))
        except Exception as e:
            d.text((x + 8, y + 100), str(e)[:40], font=FONT, fill="red")
        d.text((x, y + TH_H + 6), "%03d %s" % (si + i, os.path.basename(f)[:24]), font=FONT, fill="yellow")
    out = os.path.join(OUT, "sheet_%02d.jpg" % (si // PER + 1))
    sheet.save(out, quality=85)
    print("sheet:", out)
