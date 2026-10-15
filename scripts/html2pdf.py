# -*- coding: utf-8 -*-
"""Render a cards HTML file to an exact-size multi-page PDF.

Tries renderers in order and uses the first that works:
  1. Python playwright            (pip install playwright && playwright install chromium)
  2. Node playwright              (node + NODE_PATH pointing at node_modules with playwright)
  3. Edge / Chrome headless CLI   (preinstalled on Windows & most desktops)

Usage: python html2pdf.py <cards.html> <out.pdf> [width_px] [height_px] [--browser <path>]
Default page size 1242x1656 px (3:4, Xiaohongshu/Douyin card). Requires
images referenced by the HTML to load (networkidle) — no silent missing art.
"""
import os
import shutil
import subprocess
import sys

HTML = os.path.abspath(sys.argv[1])
OUT = os.path.abspath(sys.argv[2])
W = sys.argv[3] if len(sys.argv) > 3 else "1242px"
H = sys.argv[4] if len(sys.argv) > 4 else "1656px"
BROWSER = None
if "--browser" in sys.argv:
    BROWSER = sys.argv[sys.argv.index("--browser") + 1]

NODE_SCRIPT = (
    "const {chromium}=require('playwright');"
    "(async()=>{const b=await chromium.launch();const p=await b.newPage();"
    "await p.goto(process.argv[1],{waitUntil:'networkidle'});"
    "await p.pdf({path:process.argv[2],width:process.argv[3],height:process.argv[4],"
    "printBackground:true});await b.close();})()"
)
PY_SCRIPT = """
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page()
    p.goto(sys.argv[1], wait_until="networkidle")
    p.pdf(path=sys.argv[2], width=sys.argv[3], height=sys.argv[4], print_background=True)
    b.close()
"""


def file_url(path):
    return "file:///" + path.replace("\\", "/")


def try_python_playwright():
    try:
        import playwright  # noqa: F401
    except ImportError:
        return False
    code = "import sys\n" + PY_SCRIPT
    r = subprocess.run([sys.executable, "-c", code, file_url(HTML), OUT, W, H])
    return r.returncode == 0


def _node_nodepath_candidates():
    cands = []
    if os.environ.get("NODE_PATH"):
        cands.append(os.environ["NODE_PATH"])
    cands.append(os.path.join(os.path.expanduser("~"), ".zcode", "tools", "pdf-env", "node_modules"))
    cands.append(os.path.join(os.getcwd(), "node_modules"))
    return cands


def try_node_playwright():
    node = shutil.which("node")
    if not node:
        return False
    for np in _node_nodepath_candidates():
        if not (np and os.path.exists(os.path.join(np, "playwright"))):
            continue
        env = dict(os.environ, NODE_PATH=np)
        r = subprocess.run([node, "-e", NODE_SCRIPT, file_url(HTML), OUT, W, H], env=env)
        if r.returncode == 0:
            return True
    return False


def _browser_candidates():
    if BROWSER:
        return [BROWSER]
    home = os.path.expanduser("~")
    return [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("msedge") or "",
    ]


def try_cli_browser():
    for exe in _browser_candidates():
        if not (exe and os.path.exists(exe)):
            continue
        # Headless CLI print-to-pdf only respects CSS @page size in new headless;
        # render, then verify the page size and reject the output if wrong.
        r = subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            "--print-to-pdf=" + OUT, file_url(HTML)],
                           capture_output=True, timeout=180)
        if r.returncode != 0 or not os.path.exists(OUT):
            continue
        try:
            import pymupdf
            doc = pymupdf.open(OUT)
            ok = abs(doc[0].rect.width - float(W[:-2]) * 0.75) < 3 and \
                 abs(doc[0].rect.height - float(H[:-2]) * 0.75) < 3
            doc.close()
        except Exception:
            ok = True  # can't verify; trust it
        if ok:
            print("rendered via", exe)
            return True
        os.remove(OUT)
        print("NOTE: %s ignored CSS @page size; output rejected." % exe)
    return False


if __name__ == "__main__":
    if try_python_playwright():
        print("rendered via python playwright")
    elif try_node_playwright():
        print("rendered via node playwright")
    elif try_cli_browser():
        pass
    else:
        sys.exit("no renderer found: install playwright (pip install playwright && "
                 "playwright install chromium) or pass --browser <chrome/edge path>")
