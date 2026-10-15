# -*- coding: utf-8 -*-
"""Find and download freely-licensed photos from Wikimedia Commons.

Two modes:

  search:   python fetch_commons.py search "Fushimi Inari torii" [limit]
  download: python fetch_commons.py download "File:NAME.jpg" <outdir> [width]

Search prints one line per candidate:  filename | WxH | license | author
Pick manually — automated picking mixes up same-named places (searching one
temple can return a different temple with the same name in another city).

Download fetches a width-capped JPEG (default 1600px) and appends a line to
<outdir>/credits.tsv:  filename | author | license | source page
Keep that file; the credits go on the last card of the deck.

If upload.wikimedia.org is unreachable (some mainland-China networks),
the download is retried through the wsrv.nl image proxy, which is usually
reachable and fast from CN.
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "travel-photo-cards/1.0 (personal, non-commercial)"}


def api(params):
    q = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers=UA)
    for attempt, delay in enumerate((0, 5, 15, 30)):  # API rate-limits bursts with 429
        if delay:
            time.sleep(delay)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                print("429, retrying in %ss ..." % (delay or 5))
                continue
            raise


def strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def info(title):
    pages = api({"action": "query", "titles": title, "prop": "imageinfo",
                 "iiprop": "url|size|extmetadata", "iiurlwidth": "1600"})
    for p in pages.get("query", {}).get("pages", {}).values():
        return (p.get("imageinfo") or [None])[0]
    return None


def do_search(term, limit=6):
    res = api({"action": "query", "generator": "search",
               "gsrsearch": term + " filetype:bitmap", "gsrnamespace": 6,
               "gsrlimit": str(limit), "prop": "imageinfo",
               "iiprop": "url|size|extmetadata", "iiurlwidth": "1600"})
    pages = res.get("query", {}).get("pages", {})
    for p in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "?")
        artist = strip_html(em.get("Artist", {}).get("value", "?"))
        print("%s | %sx%s | %s | %s" % (p.get("title", "?"), ii.get("width", "?"),
                                        ii.get("height", "?"), lic, artist[:60]))


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def do_download(title, outdir, width=1600, savename=None):
    os.makedirs(outdir, exist_ok=True)
    ii = info(title)
    if not ii:
        sys.exit("no imageinfo for " + title)
    em = ii.get("extmetadata", {})
    lic = em.get("LicenseShortName", {}).get("value", "?")
    artist = strip_html(em.get("Artist", {}).get("value", "?"))
    page = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
    name = savename or os.path.basename(title)
    thumb = ii.get("thumburl") or ii.get("url")
    data = None
    try:
        data = fetch(thumb)
    except Exception as e:
        print("direct fetch failed (%s), retrying via wsrv.nl ..." % e)
        orig_path = urllib.parse.urlparse(ii.get("url")).path.lstrip("/")
        proxy = "https://wsrv.nl/?url=" + urllib.parse.quote(
            "upload.wikimedia.org/" + orig_path, safe="") + "&w=" + str(width)
        data = fetch(proxy)
    safe = re.sub(r"[^\w.\-()\u4e00-\u9fff]+", "_", name)
    if not safe.lower().endswith((".jpg", ".jpeg", ".png")):
        safe += ".jpg"
    out = os.path.join(outdir, safe)
    with open(out, "wb") as f:
        f.write(data)
    with open(os.path.join(outdir, "credits.tsv"), "a", encoding="utf-8") as f:
        f.write("%s | %s | %s | %s\n" % (safe, artist, lic, page))
    print("saved %s (%d KB)" % (out, len(data) // 1024))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        do_search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6)
    elif len(sys.argv) >= 4 and sys.argv[1] == "download":
        do_download(sys.argv[2], sys.argv[3],
                    int(sys.argv[4]) if len(sys.argv) > 4 else 1600,
                    sys.argv[5] if len(sys.argv) > 5 else None)
    else:
        sys.exit(__doc__)
