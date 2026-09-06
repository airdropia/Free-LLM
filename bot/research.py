#!/usr/bin/env python3
"""
Free-LLM research bot.

Scans the web for free LLM API offers, verifies the curated provider
knowledge base daily, discovers new leads, and writes results to:

  - README.md           (generated section between OFFERS markers)
  - results/offers.json (structured, machine-readable)
  - results/history.md  (daily snapshot log)
  - site/index.html     (GitHub Pages site)

Runs in GitHub Actions on a daily schedule. Python stdlib only - no
dependencies to install. Never crashes the workflow on a single source
failure; every source is isolated and reported in the output.
"""

import concurrent.futures
import html as html_mod
import json
import os
import random
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Config (tunable)
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
BOT_DIR = ROOT / "bot"
RESULTS_DIR = ROOT / "results"
SITE_DIR = ROOT / "site"

PROVIDERS_FILE = BOT_DIR / "providers.json"
QUERIES_FILE = BOT_DIR / "queries.txt"
OFFERS_JSON = RESULTS_DIR / "offers.json"
HISTORY_MD = RESULTS_DIR / "history.md"
SITE_HTML = SITE_DIR / "index.html"
README = ROOT / "README.md"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 "
    "Firefox/128.0 (Free-LLM research bot)"
)
TIMEOUT = 12          # seconds per HTTP request
RETRIES = 2           # extra attempts per request
VERIFY_WORKERS = 6    # parallel link checkers
MAX_DDG_QUERIES = 10  # DuckDuckGo queries per run
MAX_HN_QUERIES = 8    # Hacker News queries per run
MAX_REDDIT_QUERIES = 3
MAX_GITHUB_QUERIES = 3
MAX_NEW_LEADS = 15    # new candidate links surfaced in the report
GH_TOKEN = os.environ.get("GH_TOKEN", "")  # provided by GitHub Actions

# API compatibility labels - what an OpenAI-format client can talk to
API_LABELS = {
    "openai-completions": "OPENAI-COMPAT",
    "openai-responses": "OPENAI-COMPAT",
    "google-generative-ai": "GOOGLE API",
    "anthropic-messages": "ANTHROPIC",
    "cohere": "COHERE",
    "other": "OTHER",
}
CLIENT_READY = {"openai-completions", "openai-responses", "google-generative-ai", "anthropic-messages"}

# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------
_ctx = ssl.create_default_context()


def http_get(url, timeout=TIMEOUT, headers=None, retries=RETRIES, size_limit=2_000_000):
    """GET a URL, return (status, final_url, text, latency). Raises on failure."""
    hdrs = {"User-Agent": USER_AGENT, "Accept": "text/html,application/json,*/*"}
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=_ctx) as resp:
                body = resp.read(size_limit)
                return resp.status, resp.geturl(), body, time.time() - t0
        except urllib.error.HTTPError as e:
            # 4xx/5xx are real answers for link-verification purposes
            return e.code, url, b"", time.time() - t0
        except Exception as e:  # noqa: BLE001 - network errors are expected
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET {url} failed: {last_err}")


def fetch_json(url, headers=None):
    """GET a JSON API endpoint; returns parsed JSON or None on failure."""
    try:
        status, final, body, _ = http_get(url, headers=headers)
        if status >= 400:
            return None
        return json.loads(body.decode("utf-8", errors="replace"))
    except Exception:
        return None


def extract_title(html_text):
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.S | re.I)
    if not m:
        return ""
    return html_mod.unescape(re.sub(r"\s+", " ", m.group(1))).strip()


def classify_status(status):
    """Map an HTTP status to a link state: ok / blocked / dead / down."""
    if 200 <= status < 400:
        return "ok"
    if status == 403:
        return "blocked"   # bot detection; likely fine in a browser
    if 400 <= status < 500:
        return "dead"
    return "down"


def verify_url(url):
    """Check a URL is live. Returns dict with status, state, ok, final_url..."""
    t0 = time.time()
    try:
        status, final, body, _ = http_get(url, timeout=10, retries=1)
        state = classify_status(status)
        return {
            "url": url,
            "status": status,
            "state": state,
            "ok": state == "ok",
            "final_url": final,
            "latency": round(time.time() - t0, 1),
            "title": extract_title(body.decode("utf-8", errors="replace"))[:120] if body else "",
        }
    except Exception as e:  # noqa: BLE001
        return {
            "url": url, "status": 0, "state": "down", "ok": False, "final_url": url,
            "latency": round(time.time() - t0, 1), "title": f"unreachable ({type(e).__name__})",
        }


# --------------------------------------------------------------------------
# Search sources (each isolated; failures reported, never fatal)
# --------------------------------------------------------------------------
def search_ddg(query, max_results=8):
    """DuckDuckGo HTML search (no API key). Returns list of dicts."""
    q = urllib.parse.quote(query)
    try:
        status, final, body, _ = http_get(
            f"https://html.duckduckgo.com/html/?q={q}",
            headers={"Accept": "text/html"},
            timeout=15, retries=1,
        )
        if status >= 400:
            # fall back to the lite endpoint (less bot protection)
            status, final, body, _ = http_get(
                f"https://lite.duckduckgo.com/lite/?q={q}",
                headers={"Accept": "text/html"},
                timeout=15, retries=1,
            )
            if status >= 400:
                return []
        text = body.decode("utf-8", errors="replace")
        out = []
        blocks = re.split(r'<div class="result', text)[1:]
        for b in blocks:
            am = re.search(r'class="result__a"[^>]*href="([^"]+)"', b)
            tm = re.search(r'class="result__a"[^>]*>(.*?)</a>', b, re.S)
            sm = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', b, re.S)
            if not am:
                continue
            raw = html_mod.unescape(am.group(1))
            # DuckDuckGo wraps links in /l/?uddg=... redirects
            if "uddg=" in raw:
                uddg = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query).get("uddg", [None])[0]
                url = uddg if uddg else raw
            else:
                url = raw
            title = html_mod.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
            snippet = html_mod.unescape(re.sub(r"<[^>]+>", "", sm.group(1))).strip() if sm else ""
            if url.startswith("//"):
                url = "https:" + url
            out.append({"title": title, "url": url, "snippet": snippet[:220]})
            if len(out) >= max_results:
                break
        if not out:
            # generic fallback: any uddg-redirect anchors (lite endpoint etc.)
            for m in re.finditer(r'<a[^>]+href="([^"]*uddg=[^"]*)"[^>]*>(.*?)</a>', text, re.S | re.I):
                raw = html_mod.unescape(m.group(1))
                uddg = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query).get("uddg", [None])[0]
                if not uddg:
                    continue
                title = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
                out.append({"title": title, "url": uddg, "snippet": ""})
                if len(out) >= max_results:
                    break
        return out
    except Exception:
        return []


def search_hn(query, max_results=12):
    """Hacker News Algolia API (free, no key)."""
    q = urllib.parse.quote(query)
    data = fetch_json(
        f"https://hn.algolia.com/api/v1/search?query={q}&tags=story&hitsPerPage={max_results}"
    )
    out = []
    if data and data.get("hits"):
        for h in data["hits"]:
            out.append({
                "title": h.get("title", ""),
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}",
                "snippet": (h.get("story_text") or "")[:220],
                "points": h.get("points", 0),
                "date": h.get("created_at", ""),
            })
    return out


def search_reddit(query, max_results=10):
    """Reddit search JSON (no key; may be blocked from datacenter IPs)."""
    q = urllib.parse.quote(query)
    data = fetch_json(
        f"https://www.reddit.com/search.json?q={q}&limit={max_results}&sort=new&t=month",
        headers={"Accept": "application/json"},
    )
    out = []
    if data and data.get("data") and data["data"].get("children"):
        for c in data["data"]["children"]:
            d = c.get("data", {})
            out.append({
                "title": d.get("title", ""),
                "url": "https://www.reddit.com" + d.get("permalink", ""),
                "snippet": (d.get("selftext") or "")[:220],
                "subreddit": d.get("subreddit", ""),
                "date": d.get("created_utc", 0),
            })
    return out


def search_github(query, max_results=8):
    """GitHub repository search (uses Actions token; falls back to anonymous)."""
    q = urllib.parse.quote(query)
    headers = {"Accept": "application/vnd.github+json"}
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    data = fetch_json(
        f"https://api.github.com/search/repositories?q={q}&sort=updated&per_page={max_results}",
        headers=headers,
    )
    out = []
    if data and data.get("items"):
        for it in data["items"]:
            out.append({
                "title": it.get("full_name", ""),
                "url": it.get("html_url", ""),
                "snippet": (it.get("description") or "")[:220],
                "stars": it.get("stargazers_count", 0),
                "date": it.get("updated_at", ""),
            })
    return out


# --------------------------------------------------------------------------
# Lead extraction
# --------------------------------------------------------------------------
def domain_of(url):
    try:
        return urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def extract_leads(all_results, known_domains):
    """Collect candidate URLs from search results not already in the KB."""
    leads, seen = [], set()
    for item in all_results:
        url = item.get("url", "")
        dom = domain_of(url)
        if not url.startswith(("http://", "https://")):
            continue
        if dom in known_domains or dom in seen:
            continue
        seen.add(dom)
        leads.append({
            "title": item.get("title", "")[:140],
            "url": url,
            "domain": dom,
            "snippet": item.get("snippet", "")[:180],
            "source": item.get("_source", ""),
        })
        if len(leads) >= MAX_NEW_LEADS:
            break
    return leads


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def status_badge(v):
    state = v.get("state", "down" if not v.get("ok") else "ok")
    if state == "ok":
        return "OK"
    if state == "blocked":
        return f"BLOCKED ({v.get('status', 'err')})"
    if state == "dead":
        return f"DEAD ({v.get('status', 'err')})"
    return f"DOWN ({v.get('status', 'err')})"


def compat_badge(p):
    api = p.get("compat", {}).get("api", "other")
    return API_LABELS.get(api, "OTHER")


def api_slug(p):
    return p.get("compat", {}).get("api", "other").replace("_", "-")


def trust_label(p):
    return p.get("trust", "unknown")


def render_markdown(providers, meta, leads, source_status):
    now = meta["last_updated"]
    lines = []
    lines.append(f"\n<!-- OFFERS-START -->\n")
    lines.append(f"## Latest Offers - {now}\n")
    lines.append(f"> {meta['ok_count']} providers verified OK | {meta['dead_count']} flagged | "
                 f"{meta['compatible_count']} client-ready (OpenAI-compatible or native API) | last full run: {now}\n")
    lines.append("| Provider | Client API | Models | Limits | Signup | Expiry | Links |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in providers:
        links = []
        if p["v_website"] and p["v_website"]["ok"]:
            links.append(f"[site]({p['website']})")
        if p["v_free"] and p["v_free"]["ok"]:
            links.append(f"[free]({p['free_url']})")
        if p["v_keys"] and p["v_keys"]["ok"]:
            links.append(f"[keys]({p['key_url']})")
        if p["v_docs"] and p["v_docs"]["ok"]:
            links.append(f"[docs]({p['docs_url']})")
        link_str = " ".join(links) if links else f"**{status_badge(p['v_website'])}**"
        models = "; ".join(p["models"][:4]) + (" …" if len(p["models"]) > 4 else "")
        signup = "no-CC " + p["signup"] if not p["credit_card_required"] else "**CC** " + p["signup"]
        expiry = p["expiry"]
        lines.append(
            f"| **{p['name']}** ({p['trust']}) | {compat_badge(p)} | {models} | "
            f"{p['limits']} | {signup} | {expiry} | {link_str} |"
        )
    if leads:
        lines.append("\n### New leads (unverified, found in today's search)\n")
        for l in leads:
            lines.append(f"- [{l['title']}]({l['url']}) ({l['domain']}, via {l['source']})")
    lines.append("\n### Source status\n")
    for k, v in source_status.items():
        lines.append(f"- {k}: {v}")
    lines.append(f"\n_Last verified: {now}. Free tiers change often - check links before relying on them._\n")
    lines.append("<!-- OFFERS-END -->\n")
    return "\n".join(lines)


def render_html(providers, meta, leads, source_status):
    now = meta["last_updated"]
    cards = []
    for p in providers:
        v = p["v_website"]
        status = status_badge(v)
        status_cls = v.get("state", "down")
        links = []
        for label, key, url in (("site", "v_website", p["website"]),
                                ("free", "v_free", p["free_url"]),
                                ("keys", "v_keys", p["key_url"]),
                                ("docs", "v_docs", p["docs_url"])):
            if p[key] and p[key]["ok"]:
                links.append(f'<a class="btn" href="{html_escape(url)}" target="_blank" rel="noopener">{label}</a>')
        if not links:
            links.append(f'<span class="btn dead">DEAD</span>')
        cc = "No credit card" if not p["credit_card_required"] else "CC required"
        cards.append(f"""
<div class="card">
  <div class="card-top">
    <h3>{html_escape(p['name'])}</h3>
    <div class="badges">
      <span class="badge api api-{api_slug(p)}">{compat_badge(p)}</span>
      <span class="badge trust trust-{p['trust']}">{p['trust']}</span>
      <span class="badge status {status_cls}">{status} · {p['v_website'].get('status', '-')}</span>
    </div>
  </div>
  <p class="models">{html_escape('; '.join(p['models']))}</p>
  <p class="limits"><strong>Limits:</strong> {html_escape(p['limits'])}</p>
  <p class="meta"><strong>Signup:</strong> {html_escape(p['signup'])} ({cc}) &nbsp;·&nbsp;
     <strong>Expiry:</strong> {html_escape(p['expiry'])}</p>
  {''.join(links)}
  <p class="note">{html_escape(p.get('notes', ''))}</p>
</div>""")

    lead_html = ""
    if leads:
        lead_html = '<h2>New leads (unverified)</h2><ul>' + "".join(
            f'<li><a href="{html_escape(l["url"])}" target="_blank" rel="noopener">{html_escape(l["title"])}</a> '
            f'<span class="dim">({html_escape(l["domain"])}, via {html_escape(l["source"])})</span></li>'
            for l in leads
        ) + "</ul>"

    src_html = "".join(f"<li>{html_escape(k)}: {html_escape(v)}</li>" for k, v in source_status.items())

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Free-LLM - Daily Free LLM API Offers</title>
<style>
:root {{ --bg:#0f1117; --card:#171a23; --txt:#e6e8ee; --dim:#8b90a0; --accent:#4f8cff; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:var(--bg); color:var(--txt); font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; padding:24px; }}
header {{ max-width:1100px; margin:0 auto 18px; }}
h1 {{ font-size:26px; }} h1 span {{ color:var(--accent); }}
.sub {{ color:var(--dim); margin:6px 0 14px; }}
input#q {{ width:100%; max-width:420px; padding:10px 14px; border-radius:8px; border:1px solid #2a2f3d;
  background:var(--card); color:var(--txt); font-size:15px; }}
.grid {{ max-width:1100px; margin:0 auto; display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:14px; }}
.card {{ background:var(--card); border:1px solid #232838; border-radius:12px; padding:16px; }}
.card-top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }}
h3 {{ font-size:16px; margin-bottom:8px; }}
.badges {{ display:flex; gap:6px; flex-wrap:wrap; }}
.badge {{ font-size:11px; padding:2px 8px; border-radius:99px; white-space:nowrap; }}
.api-openai-completions, .api-openai-responses {{ background:#14304a; color:#60a5fa; }}
.api-google-generative-ai {{ background:#163a24; color:#4ade80; }}
.api-anthropic-messages {{ background:#3a1414; color:#f87171; }}
.api-cohere, .api-other {{ background:#2a2414; color:#fbbf24; }}
.trust-high {{ background:#1c2a3a; color:#7dd3fc; }}
.trust-medium {{ background:#2a2414; color:#fbbf24; }}
.trust-low {{ background:#3a1414; color:#f87171; }}
.status.ok {{ background:#163a24; color:#4ade80; }}
.status.blocked {{ background:#3a2f14; color:#facc15; }}
.status.dead, .status.down {{ background:#3a1414; color:#f87171; }}
.models {{ color:var(--txt); margin:6px 0; }}
.limits {{ color:var(--dim); font-size:13.5px; margin:6px 0; }}
.meta {{ color:var(--dim); font-size:13px; margin:6px 0; }}
.note {{ color:var(--dim); font-size:12.5px; font-style:italic; margin-top:8px; }}
.btn {{ display:inline-block; background:#232838; color:var(--txt); text-decoration:none;
  font-size:12.5px; padding:4px 12px; border-radius:6px; margin:6px 4px 0 0; }}
.btn:hover {{ background:#2f3547; }}
.btn.dead {{ background:#3a1414; color:#f87171; }}
section {{ max-width:1100px; margin:26px auto; }}
h2 {{ font-size:19px; margin-bottom:10px; }}
ul {{ margin-left:20px; }} .dim {{ color:var(--dim); font-size:13px; }}
footer {{ max-width:1100px; margin:30px auto; color:var(--dim); font-size:12.5px; }}
</style>
</head>
<body>
<header>
  <h1>Free-LLM <span>· daily free LLM API offers</span></h1>
  <p class="sub">Auto-researched daily by a GitHub Actions bot. Last run: <strong>{now}</strong> ·
     {meta['ok_count']} providers OK · {meta['dead_count']} flagged · {meta['compatible_count']} client-ready ·
     zero credit cards, email/Google/GitHub signups only (unless marked CC)</p>
  <input id="q" type="search" placeholder="Filter providers, models, limits..." autofocus>
</header>
<div class="grid" id="grid">
{''.join(cards)}
</div>
{lead_html if lead_html else ''}
<section>
  <h2>Search source status</h2>
  <ul>{src_html}</ul>
</section>
<footer>Generated by <a href="https://github.com/airdropia/Free-LLM">Free-LLM</a> research bot.
  Free tiers change frequently; always verify links before relying on an offer.
  Data is community-curated, not a guarantee.</footer>
<script>
const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const t = q.value.toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    c.style.display = c.textContent.toLowerCase().includes(t) ? '' : 'none';
  }});
}});
</script>
</body>
</html>"""


def html_escape(s):
    return html_mod.escape(str(s), quote=True)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    # This bot is meant to run only inside GitHub Actions (keeps the local
    # machine clean). Refuse local execution unless explicitly forced.
    if os.environ.get("GITHUB_ACTIONS") != "true" and "--force-local" not in sys.argv:
        print("Refusing to run outside GitHub Actions (local machine stays clean).")
        print("Run in CI, or pass --force-local to override.")
        return

    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Load knowledge base
    try:
        kb = json.loads(PROVIDERS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"FATAL: cannot read {PROVIDERS_FILE}: {e}")
        sys.exit(1)
    providers = kb.get("providers", [])
    print(f"[{now_iso}] loaded {len(providers)} providers from knowledge base")

    # 2. Run web searches
    queries = [l.strip() for l in QUERIES_FILE.read_text(encoding="utf-8").splitlines()
               if l.strip() and not l.strip().startswith("#")]
    source_status = {}
    all_results = []

    ddg_qs = queries[:MAX_DDG_QUERIES]
    ddg_ok = 0
    for i, q in enumerate(ddg_qs):
        r = search_ddg(q)
        for item in r:
            item["_source"] = "ddg"
        all_results.extend(r)
        ddg_ok += 1 if r else 0
        time.sleep(random.uniform(1.0, 2.0))
    source_status["duckduckgo"] = f"{ddg_ok}/{len(ddg_qs)} queries returned results"

    hn_qs = queries[:MAX_HN_QUERIES]
    hn_ok = 0
    for q in hn_qs:
        r = search_hn(q)
        for item in r:
            item["_source"] = "hn"
        all_results.extend(r)
        hn_ok += 1 if r else 0
    source_status["hackernews"] = f"{hn_ok}/{len(hn_qs)} queries returned results"

    rq = ["free llm api key no credit card", "free llm api credits", "free api tier llm"]
    reddit_ok = 0
    for q in rq[:MAX_REDDIT_QUERIES]:
        r = search_reddit(q)
        for item in r:
            item["_source"] = "reddit"
        all_results.extend(r)
        reddit_ok += 1 if r else 0
    source_status["reddit"] = f"{reddit_ok}/{min(MAX_REDDIT_QUERIES, len(rq))} queries returned results"

    gq = ["free llm api", "free llm api credits", "free llm providers tier"]
    gh_ok = 0
    for q in gq[:MAX_GITHUB_QUERIES]:
        r = search_github(q)
        for item in r:
            item["_source"] = "github"
        all_results.extend(r)
        gh_ok += 1 if r else 0
    source_status["github"] = f"{gh_ok}/{min(MAX_GITHUB_QUERIES, len(gq))} queries returned results"

    print(f"[{now_iso}] search returned {len(all_results)} total results")

    # 3. Verify all KB URLs in parallel
    urls_to_check = {}
    for p in providers:
        for key in ("website", "free_url", "key_url", "docs_url"):
            u = p.get(key)
            if u:
                urls_to_check[u] = (p["slug"], key)
    print(f"[{now_iso}] verifying {len(urls_to_check)} URLs (parallel, {VERIFY_WORKERS} workers)")

    verified = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=VERIFY_WORKERS) as ex:
        futures = {ex.submit(verify_url, u): u for u in urls_to_check}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            verified[res["url"]] = res

    dead = [u for u, r in verified.items() if not r["ok"]]
    print(f"[{now_iso}] verification done: {len(verified) - len(dead)} OK, {len(dead)} dead/unreachable")
    for u in dead:
        print(f"  DEAD: {u} ({verified[u]['status']})")

    # 4. Attach verification + build offers list
    for p in providers:
        p["v_website"] = verified.get(p.get("website"), {"ok": False, "status": "n/a", "url": p.get("website")})
        p["v_free"] = verified.get(p.get("free_url"), {"ok": False, "status": "n/a", "url": p.get("free_url")})
        p["v_keys"] = verified.get(p.get("key_url"), {"ok": False, "status": "n/a", "url": p.get("key_url")})
        p["v_docs"] = verified.get(p.get("docs_url"), {"ok": False, "status": "n/a", "url": p.get("docs_url")})
        p["verified_at"] = now_iso

    ok_count = sum(1 for p in providers if p["v_website"]["ok"])
    dead_count = len(providers) - ok_count
    compatible_count = sum(1 for p in providers if p.get("compat", {}).get("api") in CLIENT_READY)

    # 5. New leads (candidates outside the KB)
    known_domains = {domain_of(p.get("website", "")) for p in providers}
    leads = extract_leads(all_results, known_domains)
    print(f"[{now_iso}] {len(leads)} new leads")

    meta = {
        "last_updated": now_iso,
        "providers_count": len(providers),
        "ok_count": ok_count,
        "dead_count": dead_count,
        "compatible_count": compatible_count,
        "leads_count": len(leads),
        "sources": source_status,
    }

    # 6. Write outputs
    RESULTS_DIR.mkdir(exist_ok=True)
    SITE_DIR.mkdir(exist_ok=True)

    offers_payload = {
        "last_updated": now_iso,
        "summary": {k: meta[k] for k in ("ok_count", "dead_count", "compatible_count", "leads_count")},
        "sources": source_status,
        "offers": [
            {
                "provider": p["name"],
                "slug": p["slug"],
                "website": p["website"],
                "free_url": p["free_url"],
                "key_url": p["key_url"],
                "docs_url": p["docs_url"],
                "signup": p["signup"],
                "credit_card_required": p["credit_card_required"],
                "models": p["models"],
                "limits": p["limits"],
                "expiry": p["expiry"],
                "expiry_note": p.get("expiry_note", ""),
                "compat": p.get("compat", {}),
                "trust": p.get("trust", "unknown"),
                "notes": p.get("notes", ""),
                "verified_at": now_iso,
                "links_verified": {
                    "website": p["v_website"]["ok"],
                    "free": p["v_free"]["ok"],
                    "keys": p["v_keys"]["ok"],
                    "docs": p["v_docs"]["ok"],
                },
                "link_states": {
                    "website": p["v_website"].get("state"),
                    "free": p["v_free"].get("state"),
                    "keys": p["v_keys"].get("state"),
                    "docs": p["v_docs"].get("state"),
                },
                "website_status": p["v_website"].get("status"),
            }
            for p in providers
        ],
        "new_leads": leads,
    }
    OFFERS_JSON.write_text(json.dumps(offers_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{now_iso}] wrote {OFFERS_JSON}")

    # History log (keep latest first, cap at 90 entries)
    history_line = f"- {now_iso} | providers={len(providers)} | ok={ok_count} | dead={dead_count} | client-ready={compatible_count} | leads={len(leads)}\n"
    prev_history = HISTORY_MD.read_text(encoding="utf-8") if HISTORY_MD.exists() else ""
    prev_lines = prev_history.splitlines()[:90]
    HISTORY_MD.write_text(history_line + "\n".join(prev_lines) + ("\n" if prev_lines else ""), encoding="utf-8")

    # README section
    md = render_markdown(providers, meta, leads, source_status)
    if README.exists():
        text = README.read_text(encoding="utf-8")
        if "<!-- OFFERS-START -->" in text and "<!-- OFFERS-END -->" in text:
            head, tail = text.split("<!-- OFFERS-START -->", 1)
            _, tail = tail.split("<!-- OFFERS-END -->", 1)
            new_text = head + md + tail
        else:
            new_text = text.rstrip() + "\n" + md
        README.write_text(new_text, encoding="utf-8")
    else:
        README.write_text(md, encoding="utf-8")
    print(f"[{now_iso}] updated {README}")

    # Pages site
    SITE_HTML.write_text(render_html(providers, meta, leads, source_status), encoding="utf-8")
    print(f"[{now_iso}] wrote {SITE_HTML}")

    print(f"[{now_iso}] DONE - summary: "
          f"{json.dumps({k: meta[k] for k in ('ok_count', 'dead_count', 'compatible_count', 'leads_count')})}")


if __name__ == "__main__":
    main()
