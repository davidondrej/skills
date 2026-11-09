#!/usr/bin/env python3
"""Scrape expert essays via DeepAPI and save each as a clean verbatim text file.

usage: fetch-sources.py --expert "Paul Graham" --out essays/paul-graham [--start 1] [--max-chars 300000] URL...
Output: <out>/NN-slug.md with a header (title, source, author, scrape date) + cleaned text.
Uses curl (not urllib) because the sandbox proxy truncates chunked responses to Python's http client.
"""
import argparse, datetime, json, os, re, subprocess, sys, time, uuid

def load_env():
    if os.environ.get("DEEPAPI_API_KEY") and os.environ.get("DEEPAPI_API_BASE_URL"):
        return
    p = os.path.expanduser("~/.deepapi/env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line.startswith("export "): line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1); os.environ.setdefault(k, v.strip().strip('"').strip("'"))
    if not os.environ.get("DEEPAPI_API_KEY"):
        sys.exit("DEEPAPI_API_KEY not set. Run: source ~/.deepapi/env")

def curl(method, path, body=None):
    base = os.environ["DEEPAPI_API_BASE_URL"].rstrip("/")
    cmd = ["curl", "-s", "-m", "180", "-X", method, path if path.startswith("http") else base + path,
           "-H", f"Authorization: Bearer {os.environ['DEEPAPI_API_KEY']}", "-H", f"Idempotency-Key: {uuid.uuid4()}"]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try: return json.loads(out)
    except json.JSONDecodeError: sys.exit(f"non-JSON response from {path}: {out[:300]}")

def scrape(urls, max_chars):
    r = curl("POST", "/v1/scrape/website", {"urls": urls, "maxDepth": 0, "maxChars": max_chars, "waitForFinishSecs": 60})
    while r.get("output") is None and r.get("status") not in ("failed",) and r.get("next", {}).get("method") == "GET":
        time.sleep(r["next"].get("afterSecs", 5)); r = curl("GET", r["next"]["path"])
    if r.get("status") == "failed" or r.get("output") is None:
        sys.exit(f"scrape failed: {json.dumps(r.get('error'))[:500]}")
    return r["output"]

def clean(text, title=""):
    out = []
    for l in text.splitlines():
        s = l.strip()
        if s.startswith("|"):                      # site layout tables: nav, ads, translation links, title cells
            c = s.strip("|").strip()
            if re.fullmatch(r"[-\s|]*", c) or len(c) < 60: continue   # separators and short nav/ad cells
            l = c                                   # long cell = real prose that the site wrapped in a table
        elif s.endswith(" |"): l = l.rstrip()[:-2]   # prose line that closes a layout cell
        if re.fullmatch(r"!\[[^\]]*\]\([^)]*\)", l.strip()): continue   # bare images
        out.extend(x.rstrip() for x in l.replace("<br>", "\n").split("\n"))
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    if title and body.startswith(title): body = body[len(title):].lstrip()   # title already in the header
    return body

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expert", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=None, help="first file number (default: continue numbering in --out)")
    ap.add_argument("--max-chars", type=int, default=300000); ap.add_argument("urls", nargs="+")
    a = ap.parse_args(); load_env(); os.makedirs(a.out, exist_ok=True)
    existing = sorted(f for f in os.listdir(a.out) if re.match(r"\d\d-.*\.md$", f))
    n = a.start or (int(existing[-1][:2]) + 1 if existing else 1)
    pages = {p.get("url"): p for p in scrape(a.urls, a.max_chars)}
    today = datetime.date.today().strftime("%d-%m-%Y")
    for u in a.urls:
        p = pages.get(u) or next((v for k, v in pages.items() if k and k.rstrip("/") == u.rstrip("/")), None)
        if not p: print(f"MISSING: {u}"); continue
        title = (p.get("title") or u).strip(); body = clean(p.get("text") or p.get("markdown") or "", title)
        path = os.path.join(a.out, f"{n:02d}-{slug(title)}.md")
        with open(path, "w") as fh:
            fh.write(f"# {title}\n\nSource: {u}\nAuthor: {a.expert}\nScraped: {today} via DeepAPI (raw text, unedited)\n\n---\n\n{body}\n")
        print(f"{path}  {len(body)} chars{'  TRUNCATED' if p.get('truncated') else ''}")
        print(f"  head: {body[:90]!r}\n  tail: {body[-90:]!r}")
        n += 1

if __name__ == "__main__": main()
