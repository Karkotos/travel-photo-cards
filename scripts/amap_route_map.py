# -*- coding: utf-8 -*-
"""Stitch AMap tiles and draw a travel-route overlay (config-file driven).

Usage: python amap_route_map.py <config.json> [--out path]

config.json keys:
  name      output base name
  extent    [lon0, lat0, lon1, lat1]   (lon0<lon1, lat0<lat1)
  zoom      tile zoom (pick so width lands ~1200-2400 px)
  scale     overlay supersample (2 = crisp text)
  cities    {name: [lon, lat]}          route stop markers + labels
  route     [[lon, lat], ...]           dashed polyline in travel order
  nights    [[label, lon, lat], ...]    day badges (D1, D2, ...)
  segments  [[text, lon, lat], ...]     distance labels
  provinces [[text, x, y], ...]         optional big faint labels, 1x px

Output defaults to images/<name>.png under the cwd. Tiles come from AMap
(webrd01-04.is.autonavi.com) — reachable from mainland China without a key.
Text needs a paper-color halo (stroke behind fill) or it collides with map
labels into unreadable mush: keep labels sparse.
"""
import io
import json
import math
import os
import ssl
import sys
import urllib.request

from PIL import Image, ImageDraw

from fontpick import pick

cfgp = sys.argv[1]
out_override = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
with open(cfgp, encoding="utf-8") as f:
    C = json.load(f)

NAME = C["name"]
LON0, LAT0, LON1, LAT1 = C["extent"]
Z = int(C["zoom"])
SCALE = int(C.get("scale", 2))
CITIES = {k: tuple(v) for k, v in C.get("cities", {}).items()}
ROUTE = [tuple(p) for p in C.get("route", [])]
NIGHTS = [tuple(x) for x in C.get("nights", [])]
SEGMENTS = [tuple(x) for x in C.get("segments", [])]
PROVINCES = [tuple(x) for x in C.get("provinces", [])]
OUT = out_override or os.path.join("images", NAME + ".png")
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)


def ll2px(lon, lat, z=Z):
    n = 2 ** z * 256.0
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


XW, YN = ll2px(LON0, LAT1)
XE, YS = ll2px(LON1, LAT0)
W, H = int(XE - XW), int(YS - YN)
CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (personal map)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
        return r.read()


tx0, tx1 = int(XW // 256), int(XE // 256)
ty0, ty1 = int(YN // 256), int(YS // 256)
canvas = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256), "#dde6ea")
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        for sub in ("webrd01", "webrd02", "webrd03", "webrd04"):
            try:
                url = f"https://{sub}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={tx}&y={ty}&z={Z}"
                got = Image.open(io.BytesIO(fetch(url))).convert("RGB")
                canvas.paste(got, ((tx - tx0) * 256, (ty - ty0) * 256))
                break
            except Exception:
                continue
img = canvas.crop((int(XW - tx0 * 256), int(YN - ty0 * 256),
                   int(XW - tx0 * 256) + W, int(YN - ty0 * 256) + H))
img = img.resize((W * SCALE, H * SCALE), Image.LANCZOS)
d = ImageDraw.Draw(img, "RGBA")


def P(lon, lat):
    x, y = ll2px(lon, lat)
    return ((x - XW) * SCALE, (y - YN) * SCALE)


f_km = pick(30, bold=True)
f_city = pick(40, bold=True)
f_badge = pick(44, bold=True)
HALO = (251, 250, 248, 230)


def halo(xy, s, fnt, fill, anchor="mm", r=5):
    x, y = xy
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx or dy:
                d.text((x + dx, y + dy), s, font=fnt, fill=HALO, anchor=anchor)
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)


def dashed(p1, p2, dash=13, gap=9, width=6, fill=(43, 110, 138, 255)):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    s, on = 0.0, True
    while s < dist:
        e = min(s + (dash if on else gap), dist)
        if on:
            d.line([x1 + ux * s, y1 + uy * s, x1 + ux * e, y1 + uy * e], fill=fill, width=width)
        s = e
        on = not on


pts = [P(*p) for p in ROUTE]
for i in range(len(pts) - 1):
    dashed(pts[i], pts[i + 1])

for day, lon, lat in NIGHTS:
    x, y = P(lon, lat)
    bw, bh = 76, 58
    d.rounded_rectangle([x - bw / 2, y - bh / 2 - 46, x + bw / 2, y + bh / 2 - 46], 8, fill=(96, 87, 60, 235))
    d.text((x, y - 46), day, font=f_badge, fill="white", anchor="mm")

for name, (lon, lat) in CITIES.items():
    x, y = P(lon, lat)
    d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(34, 34, 31, 255))
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(245, 241, 232, 255))
    halo((x + 26, y - 22), name, f_city, (34, 34, 31, 255), anchor="la")

for s_, lon, lat in SEGMENTS:
    halo(P(lon, lat), s_, f_km, (43, 110, 138, 255))

if PROVINCES:
    prov_font = pick(84)
    for s_, x, y in PROVINCES:
        d.text((x * SCALE, y * SCALE), s_, font=prov_font, fill=(150, 140, 110, 80), anchor="mm")

img.save(OUT)
print("saved", OUT, img.size)
