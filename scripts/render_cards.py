# -*- coding: utf-8 -*-
"""Render a multi-card PDF to same-size PNGs (dpi=96 -> exact CSS px per page).

Usage: python render_cards.py <cards.pdf> <outdir> [name_prefix]
"""
import os
import sys

import pymupdf

PDF = sys.argv[1]
OUT = sys.argv[2]
PREFIX = sys.argv[3] if len(sys.argv) > 3 else "card"
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(PDF)
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=96)
    pix.save(os.path.join(OUT, "%s%02d.png" % (PREFIX, i + 1)))
print("pages:", len(doc), "size:", pix.width, "x", pix.height)
doc.close()
