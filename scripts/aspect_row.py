# -*- coding: utf-8 -*-
"""Aspect-aware photo row generator.

Reads real image dimensions so every slot matches the photo's natural
aspect ratio (portrait in tall slots, landscape in wide slots). Photos
that don't fit a row should be DROPPED, never squeezed — a weird crop
is worse than one fewer image.

Usage:
    from aspect_row import gen_row
    html = gen_row(rels, container=1074, gap=20, cap=560, base="photos_work", prefix="photos_work")
    # rels: filenames inside base; prefix: URL prefix used in <img src>
    # Returns a <div> row where each box height = min(natural fill, cap)
    # and each width = height * (w/h) — zero distortion, zero crop.
"""
import os

from PIL import Image


def ratio(rel, base):
    im = Image.open(os.path.join(base, rel))
    return im.size[0] / im.size[1]


def gen_row(rels, container=1074, gap=20, cap=560, base="photos_work", prefix="photos_work", margin="22px 84px 0"):
    rs = [ratio(r, base) for r in rels]
    H = (container - gap * (len(rels) - 1)) / sum(rs)
    H = min(H, cap)
    inner = ""
    for r, rel in zip(rs, rels):
        w = int(H * r)
        inner += f'      <img class="ph" src="{prefix}/{rel}" style="width:{w}px; height:{int(H)}px;" alt="">\n'
    return f'    <div style="display:flex; gap:{gap}px; margin:{margin};">\n{inner}    </div>'


def hero_pair(rel_a, rel_b, container=1074, gap=20, base="photos_work", prefix="photos_work"):
    """Two photos at equal height, widths from natural ratios."""
    ra, rb = ratio(rel_a, base), ratio(rel_b, base)
    H = (container - gap) / (ra + rb)
    wa, wb = int(H * ra), int(H * rb)
    return (f'    <div style="display:flex; gap:{gap}px; margin-top:34px;">\n'
            f'      <img class="ph" src="{prefix}/{rel_a}" style="width:{wa}px; height:{int(H)}px;" alt="">\n'
            f'      <img class="ph" src="{prefix}/{rel_b}" style="width:{wb}px; height:{int(H)}px;" alt="">\n'
            f'    </div>')


if __name__ == "__main__":
    print(gen_row(["sample/a.jpg", "sample/b.jpg"], base=".", prefix="."))
