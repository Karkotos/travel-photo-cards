# -*- coding: utf-8 -*-
"""Rename card PNGs to publish names and zip them.

Usage: python package_cards.py <png_dir> <names.txt> <out_dir>

names.txt: one publish name per line (UTF-8, e.g. 01_封面.png), in deck
order; line count must equal the PNG count. cards.html / cards.pdf next to
the PNGs are bundled into the zip for future edits.
"""
import os
import shutil
import sys
import zipfile

SRC, NAMES, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ZIP = OUT + ".zip"

with open(NAMES, encoding="utf-8") as f:
    names = [ln.strip() for ln in f if ln.strip()]

files = sorted(f2 for f2 in os.listdir(SRC) if f2.endswith(".png"))
if len(files) != len(names):
    sys.exit("mismatch: %d pngs vs %d names" % (len(files), len(names)))

if os.path.exists(OUT):
    shutil.rmtree(OUT)
if os.path.exists(ZIP):
    os.remove(ZIP)
os.makedirs(OUT)
for f2, n in zip(files, names):
    shutil.copy2(os.path.join(SRC, f2), os.path.join(OUT, n))

for extra, dest in (("cards.html", "cards_source.html"), ("cards.pdf", "cards_preview.pdf")):
    p = os.path.join(os.path.dirname(SRC) or ".", extra)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(OUT, dest))

with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, fs in os.walk(OUT):
        for f2 in fs:
            p = os.path.join(root, f2)
            z.write(p, os.path.relpath(p, os.path.dirname(OUT)))
print("zip:", ZIP, round(os.path.getsize(ZIP) / 1048576, 1), "MB")
