# -*- coding: utf-8 -*-
"""Make upright, downscaled work copies for card building.

Mobile originals often carry an EXIF rotation flag; saving without
transposing first leaves them sideways in the rendered cards. This also
caps the long edge (default 2000px) so the HTML renderer never chokes on
50MP originals.

Usage: python prep_photos.py <src_dir> <work_dir> [max_edge]
Prints one "name | WxH" line per file — feed these real dimensions into
slot math (aspect_row.py), never eyeball them.
"""
import os
import sys

from PIL import Image, ImageOps

src = sys.argv[1]
work = sys.argv[2]
max_edge = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
os.makedirs(work, exist_ok=True)

for root, _, fs in os.walk(src):
    for f in sorted(fs):
        if not f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue
        p = os.path.join(root, f)
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        if max(im.size) > max_edge:
            im.thumbnail((max_edge, max_edge), Image.LANCZOS)
        out = os.path.join(work, os.path.splitext(f)[0] + ".jpg")
        im.save(out, quality=92)
        print("%s | %dx%d" % (os.path.basename(out), *im.size))
