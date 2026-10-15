# -*- coding: utf-8 -*-
"""Cross-platform CJK font picker for PIL.

Usage:
    from fontpick import pick
    font = pick(28, bold=True)
"""
import os

from PIL import ImageFont

_CANDIDATES = [
    # Windows
    (r"C:\Windows\Fonts\msyhbd.ttc", True),
    (r"C:\Windows\Fonts\msyh.ttc", False),
    (r"C:\Windows\Fonts\simhei.ttf", True),
    # macOS
    ("/System/Library/Fonts/PingFang.ttc", None),
    ("/System/Library/Fonts/STHeiti Light.ttc", None),
    # Linux (common Noto CJK locations)
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", True),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", False),
    ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", False),
]


def pick(size, bold=False):
    for path, is_bold in _CANDIDATES:
        if is_bold is not None and bold != bool(is_bold):
            continue
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    for path, _ in _CANDIDATES:  # any CJK family beats the bitmap default
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()
