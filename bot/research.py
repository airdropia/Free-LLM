#!/usr/bin/env python3
"""
Free-LLM research bot - aggressive third-party provider discovery.

Focus: FRESH third-party LLM API providers/routers and their free offers
(often 1-2 week frontier-model freebies). Official big-name providers are
explicitly excluded from tracking (their generic quotas are not useful).

What it does every run:

  1. Searches many sources (Bing, SearXNG, Google News, Hacker News,
     Reddit-archive (pullpush), Lobsters, GitHub, Telegram, X/Nitter).
  2. Scores candidate "leads" by keyword relevance.
  3. AUTO-DISCOVERS: assesses top leads - if the site is live, speaks API
     and offers free/credit/trial access, and is not an official provider,
     it is AUTO-ADDED to the knowledge base (providers.json) and committed
     back to the repo.
  4. Verifies every tracked provider's links daily (OK / BLOCKED / DEAD / DOWN).
  5. Writes results to README.md, results/offers.json, results/leads.json,
     results/history.md and site/index.html (GitHub Pages).

Runs in GitHub Actions. Python stdlib only. Never crashes on a single
source failure - each source is isolated and reported.
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
LEADS_JSON = RESULTS_DIR / "leads.json"
HISTORY_MD = RESULTS_DIR / "history.md"
SITE_HTML = SITE_DIR / "index.html"
README = ROOT / "README.md"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 "
    "Firefox/128.0 (Free-LLM research bot)"
)
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
TIMEOUT = 12
RETRIES = 2
VERIFY_WORKERS = 6

MAX_BING_QUERIES = 12      # Bing web search
MAX_SEARXNG_QUERIES = 8    # SearXNG (JSON, multi-instance)
MAX_HN_QUERIES = 14        # Hacker News
MAX_REDDIT_QUERIES = 5     # Reddit via pullpush archive API
MAX_GITHUB_QUERIES = 5     # GitHub repo search
MAX_NEWS_QUERIES = 8       # Google News RSS
MAX_LOBS_QUERIES = 1       # Lobsters newest (single fetch)
MAX_TELEGRAM_CHANNELS = 5  # Telegram public channels
MAX_NITTER_QUERIES = 2     # X/Twitter via Nitter (best effort)
MAX_NEW_LEADS = 40         # leads surfaced in the report
MAX_AUTO_ADD_PER_RUN = 8   # new providers auto-added per run
MAX_TOTAL_PROVIDERS = 60   # cap on tracked providers (auto-prune)

GH_TOKEN = os.environ.get("GH_TOKEN", "")  # provided by GitHub Actions

# API compatibility labels
API_LABELS = {
    "openai-completions": "OPENAI-COMPAT",
    "openai-responses": "OPENAI-COMPAT",
    "google-generative-ai": "GOOGLE API",
    "anthropic-messages": "ANTHROPIC",
    "cohere": "COHERE",
    "other": "OTHER",
}

# Lead relevance keywords - aggressive discovery
SCORE_KEYWORDS = [
    "free", "api key", "api keys", "credits", "credit", "tokens", "trial",
    "offer", "promo", "promotion", "coupon", "giveaway", "frontier",
    "router", "gateway", "aggregator", "proxy", "access", "signup",
    "register", "new", "launch", "startup", "unlimited", "unmetered",
    "discount", "deal", "week", "month", "limited", "key", "api",
]
STRONG_SIGNALS = ("free", "credit", "trial", "offer", "promo", "coupon",
                  "giveaway", "api key", "unlimited", "unmetered")

# LLM-specific page signals - prevents crypto/DEX/finance false positives
LLM_SIGNALS = ("llm", " gpt", "gpt-", "claude", "gemini", "grok", "llama", "qwen",
               "deepseek", "mistral", "kimi", "glm", "chat completions",
               "chat/completions", "assistant api", "language model")

# SearXNG public instances (JSON API, no key) - first working wins
SEARXNG_INSTANCES = [
    "https://searx.be",
    "https://search.bus-hit.me",
    "https://paulgo.io",
    "https://searx.tiekoetter.com",
    "https://searxng.site",
]

# Telegram public channels to scan (t.me/s/<channel> preview, no auth).
# Only channels that actually exist produce content; dead ones are skipped.
TELEGRAM_CHANNELS = [
    "aibrews",
    "free_api_keys",
    "llmapi",
    "AI_Deals",
    "freeapis",
]

# X/Twitter via public Nitter instances (best effort, first working wins)
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.poast.org",
    "https://nitter.privacyredirect.com",
    "https://nitter.space",
    "https://lightbrd.com",
    "https://nitter.1d4.us",
]

# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------
_ctx = ssl.create_default_context()


def http_get(url, timeout=TIMEOUT, headers=None, retries=RETRIES, size_limit=2_000_000):
    """GET a URL, return (status, final_url, body, latency). Raises on failure."""
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
            return e.code, url, b"", time.time() - t0
        except Exception as e:  # noqa: BLE001
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
    if 200 <= status < 400:
        return "ok"
    if status == 403:
        return "blocked"
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
def search_bing(query, max_results=8):
    """Bing web search HTML scrape (no key)."""
    q = urllib.parse.quote(query)
    try:
        status, final, body, _ = http_get(
            f"https://www.bing.com/search?q={q}&count=20",
            headers={"User-Agent": BROWSER_UA, "Accept": "text/html"},
            timeout=15, retries=1,
        )
        if status >= 400:
            return []
        text = body.decode("utf-8", errors="replace")
        out = []
        for b in re.split(r'<li class="b_algo"', text)[1:]:
            am = re.search(r'<h2[^>]*><a[^>]+href="([^"]+)"', b)
            tm = re.search(r"<h2[^>]*><a[^>]*>(.*?)</a>", b, re.S)
            sm = re.search(r"<p[^>]*>(.*?)</p>", b, re.S)
            if not am:
                continue
            url = html_mod.unescape(am.group(1))
            title = html_mod.unescape(re.sub(r"<[^>]+>", "", tm.group(1))).strip() if tm else ""
            snippet = html_mod.unescape(re.sub(r"<[^>]+>", "", sm.group(1))).strip() if sm else ""
            out.append({"title": title, "url": url, "snippet": snippet[:220]})
            if len(out) >= max_results:
                break
        return out
    except Exception:
        return []


def search_searxng(query, max_results=8):
    """SearXNG JSON (no key) across public instances."""
    q = urllib.parse.quote(query)
    for inst in SEARXNG_INSTANCES:
        try:
            status, final, body, _ = http_get(
                f"{inst}/search?q={q}&format=json",
                headers={"Accept": "application/json"},
                timeout=12, retries=1,
            )
            if status >= 400:
                continue
            data = json.loads(body.decode("utf-8", errors="replace"))
            out = []
            for r in (data.get("results") or [])[:max_results]:
                out.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": (r.get("content") or "")[:220],
                })
            if out:
                return out
        except Exception:
            continue
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


def search_reddit_pullpush(query, max_results=10):
    """Reddit submissions via pullpush.io archive (free, no key)."""
    q = urllib.parse.quote(query)
    data = fetch_json(
        f"https://api.pullpush.io/reddit/search/submission/?q={q}&size={max_results}&sort=desc"
    )
    out = []
    if data and data.get("data"):
        for d in data["data"]:
            out.append({
                "title": d.get("title", ""),
                "url": "https://www.reddit.com" + (d.get("permalink") or ""),
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


def search_google_news(query, max_results=8):
    """Google News RSS (no key, datacenter-friendly)."""
    q = urllib.parse.quote(query)
    try:
        status, final, body, _ = http_get(
            f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en",
            headers={"Accept": "application/rss+xml"},
            timeout=15, retries=1,
        )
        if status >= 400:
            return []
        text = body.decode("utf-8", errors="replace")
        out = []
        for m in re.finditer(r"<item>(.*?)</item>", text, re.S):
            tm = re.search(r"<title>(.*?)</title>", m.group(1), re.S)
            lm = re.search(r"<link>(.*?)</link>", m.group(1), re.S)
            sm = re.search(r"<description>(.*?)</description>", m.group(1), re.S)
            if not lm:
                continue
            out.append({
                "title": html_mod.unescape(tm.group(1)) if tm else "",
                "url": html_mod.unescape(lm.group(1)),
                "snippet": html_mod.unescape(re.sub(r"<[^>]+>", "", sm.group(1)))[:220] if sm else "",
            })
            if len(out) >= max_results:
                break
        return out
    except Exception:
        return []


def search_lobsters(max_results=40):
    """Lobste.rs newest stories JSON (no key)."""
    data = fetch_json("https://lobste.rs/newest.json")
    out = []
    if data:
        for it in data:
            out.append({
                "title": it.get("title", ""),
                "url": it.get("url") or f"https://lobste.rs/{it.get('short_id', '')}",
                "snippet": "",
                "date": it.get("created_at", ""),
            })
            if len(out) >= max_results:
                break
    return out


def search_telegram(channels, max_results=12):
    """Telegram public channel previews via t.me/s/<channel> (no auth)."""
    out = []
    for ch in channels:
        try:
            status, final, body, _ = http_get(
                f"https://t.me/s/{ch}",
                headers={"User-Agent": BROWSER_UA, "Accept": "text/html"},
                timeout=12, retries=1,
            )
            if status >= 400:
                continue
            text = body.decode("utf-8", errors="replace")
            msgs = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', text, re.S)
            for m in msgs[:max_results]:
                clean = html_mod.unescape(re.sub(r"<[^>]+>", " ", m)).strip()
                if not clean:
                    continue
                if not any(k in clean.lower() for k in ("free", "api", "credit", "key", "trial")):
                    continue
                lm = re.search(r'href="(https?://[^"]+)"', m)
                url = html_mod.unescape(lm.group(1)) if lm else f"https://t.me/s/{ch}"
                out.append({"title": f"[TG:{ch}] {clean[:120]}", "url": url, "snippet": clean[:220]})
            if out and len(out) >= max_results:
                break
        except Exception:
            continue
    return out


def search_nitter_x(query, max_results=10):
    """X/Twitter search via public Nitter instances (best effort)."""
    q = urllib.parse.quote(query)
    results = []
    for inst in NITTER_INSTANCES:
        try:
            status, final, body, _ = http_get(
                f"{inst}/search?f=tweets&q={q}",
                headers={"Accept": "text/html"},
                timeout=12, retries=1,
            )
            if status >= 400:
                continue
            text = body.decode("utf-8", errors="replace")
            links = re.findall(r'<a class="tweet-link" href="([^"]+)"', text)
            contents = re.findall(r'<div class="tweet-content[^>]*>(.*?)</div>', text, re.S)
            if not contents:
                continue
            for i, c in enumerate(contents[:max_results]):
                txt = html_mod.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                if not txt:
                    continue
                href = links[i] if i < len(links) else ""
                if href:
                    url = href if href.startswith("http") else f"{inst}{href}"
                else:
                    m = re.search(r"https?://[^\s)]+", txt)
                    url = m.group(0) if m else f"{inst}/search?q={q}"
                results.append({"title": txt[:140], "url": url, "snippet": txt[:220]})
            if results:
                break
        except Exception:
            continue
    return results


# --------------------------------------------------------------------------
# Lead scoring & discovery
# --------------------------------------------------------------------------
def domain_of(url):
    try:
        return urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def score_lead(text):
    """Score a lead by keyword hits. Returns (score, matched_keywords)."""
    text = text.lower()
    hits = [k for k in SCORE_KEYWORDS if k in text]
    return len(hits), hits[:8]


def extract_leads(all_results, known_domains):
    """Collect candidate URLs not already in the KB, best per domain, sorted."""
    best_by_domain = {}
    for item in all_results:
        url = item.get("url", "")
        dom = domain_of(url)
        if not url.startswith(("http://", "https://")) or not dom:
            continue
        if dom in known_domains:
            continue
        text = f"{item.get('title', '')} {item.get('snippet', '')} {dom}".lower()
        score, hits = score_lead(text)
        has_strong = any(s in text for s in STRONG_SIGNALS)
        if not (has_strong and "api" in text) and score < 2:
            continue
        rec = {
            "title": item.get("title", "")[:140],
            "url": url,
            "domain": dom,
            "snippet": item.get("snippet", "")[:180],
            "source": item.get("_source", ""),
            "score": score,
            "hits": hits,
        }
        if dom not in best_by_domain or score > best_by_domain[dom]["score"]:
            best_by_domain[dom] = rec
    return sorted(best_by_domain.values(), key=lambda x: -x["score"])[:MAX_NEW_LEADS]


def assess_lead(lead, known_domains, blocklist, news_domains):
    """Authenticity check for auto-adding a lead as a tracked provider."""
    dom = lead["domain"]
    if dom in known_domains or dom in blocklist or dom in news_domains:
        return None
    url = f"https://{dom}"
    reasons = []
    status = 0
    text = ""
    try:
        status, final, body, _ = http_get(url, timeout=12, retries=1)
        if status >= 400:
            reasons.append(f"homepage HTTP {status}")
            # fallback: fetch through the free r.jina.ai reader proxy
            try:
                s2, _, b2, _ = http_get(f"https://r.jina.ai/{url}", timeout=18, retries=1)
                if s2 < 400:
                    status, body, text = 200, b2, b2.decode("utf-8", errors="replace")
                    reasons.append("read via r.jina.ai")
            except Exception:
                pass
        else:
            text = body.decode("utf-8", errors="replace")
    except Exception:
        return {"add": False, "reasons": ["homepage unreachable"]}
    if status >= 400:
        return {"add": False, "reasons": reasons}

    low = text.lower()
    signals = []
    llm_hit = any(k in low for k in LLM_SIGNALS)
    if "api" in low:
        signals.append("mentions api")
    if any(k in low for k in ("free", "credit", "trial", "signup", "promo", "coupon")):
        signals.append("free/credit/trial signal")
    if any(k in low for k in ("api key", "chat/completions", "openai", "v1/models", "bearer")):
        signals.append("key/completions signal")
    if llm_hit:
        signals.append("llm/model signal")
    if llm_hit and len(signals) >= 3:
        reasons += signals
        reasons.append(f"homepage reachable ({status})")
        return {"add": True, "reasons": reasons, "status": status}
    return {"add": False, "reasons": reasons or ["no api/free signals on page"]}


def clean_name(title, dom):
    """Derive a tidy provider name from a lead title, falling back to domain."""
    t = (title or "").strip()
    for pre in ("Show HN:", "Show HN :", "Launch HN:", "Ask HN:", "HN:"):
        if t.startswith(pre):
            t = t[len(pre):].strip()
            break
    if len(t) < 3 or len(t) > 55:
        return dom
    return t[:55]


def build_provider(lead, assess, now_iso):
    dom = lead["domain"]
    return {
        "name": clean_name(lead.get("title"), dom),
        "slug": dom.replace(".", "-")[:50],
        "website": f"https://{dom}",
        "free_url": lead["url"] if lead["url"].startswith("https://") else f"https://{dom}",
        "key_url": "",
        "docs_url": "",
        "signup": "email",
        "credit_card_required": False,
        "models": ["see website"],
        "limits": "see website",
        "expiry": "unknown",
        "expiry_note": "Auto-discovered; verify before relying on it",
        "compat": {"api": "openai-completions", "notes": "auto-discovered; verify endpoint"},
        "trust": "medium",
        "notes": f"Auto-discovered {now_iso[:10]} via {lead['source']}",
        "auto": True,
        "discovered_at": now_iso,
        "discovery_signals": assess["reasons"],
    }


def prune_providers(providers, verified, max_total=MAX_TOTAL_PROVIDERS):
    """Keep the list under the cap: drop dead auto-added providers first."""
    if len(providers) <= max_total:
        return providers
    auto = sorted([p for p in providers if p.get("auto")], key=lambda p: p.get("discovered_at", ""))
    for p in auto:
        if len(providers) <= max_total:
            break
        v = verified.get(p.get("website"))
        if v and not v["ok"]:
            providers.remove(p)
    for p in auto:
        if len(providers) <= max_total:
            break
        providers.remove(p)
    return providers


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


def render_markdown(providers, meta, leads, source_status, auto_added):
    now = meta["last_updated"]
    lines = []
    lines.append("\n<!-- OFFERS-START -->\n")
    lines.append(f"## Latest Third-Party Offers - {now}\n")
    lines.append(f"> {meta['ok_count']} providers verified OK | {meta['dead_count']} flagged | "
                 f"{meta['auto_added_count']} auto-discovered this run | last full run: {now}\n")
    if auto_added:
        lines.append("\n### ✨ Auto-discovered this run (new providers added)\n")
        for a in auto_added:
            lines.append(f"- **{a['name']}** (`{a['domain']}`) — {', '.join(a['reasons'])}")
        lines.append("")
    lines.append("\n| Provider | Client API | Models | Limits | Signup | Expiry | Links |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in providers:
        links = []
        for label, key, url in (("site", "v_website", p["website"]),
                                ("free", "v_free", p["free_url"]),
                                ("keys", "v_keys", p["key_url"]),
                                ("docs", "v_docs", p["docs_url"])):
            if p.get(key) and p[key]["ok"] and url:
                links.append(f"[{label}]({url})")
        link_str = " ".join(links) if links else f"**{status_badge(p.get('v_website', {'ok': False}))}**"
        models = "; ".join(p["models"][:3]) + (" …" if len(p["models"]) > 3 else "")
        signup = "no-CC " + p["signup"] if not p.get("credit_card_required", True) else "**CC?** " + p["signup"]
        expiry = p["expiry"]
        mark = " ⚡" if p.get("discovered_at", "") == meta["last_updated"] else (" ↻" if p.get("auto") else "")
        lines.append(
            f"| **{p['name']}**{mark} ({p['trust']}) | {compat_badge(p)} | {models} | "
            f"{p['limits']} | {signup} | {expiry} | {link_str} |"
        )
    if leads:
        lines.append("\n### New leads (unverified, found in today's search)\n")
        for l in leads:
            lines.append(
                f"- [{l['title']}]({l['url']}) ({l['domain']}, via {l['source']}, "
                f"score {l['score']}: {', '.join(l['hits'])})\n"
            )
    lines.append("### Source status\n")
    for k, v in source_status.items():
        lines.append(f"- {k}: {v}")
    lines.append(f"\n_Last verified: {now}. Offers change fast - verify links before relying on them._\n")
    lines.append("<!-- OFFERS-END -->\n")
    return "\n".join(lines)


def render_html(providers, meta, leads, source_status, auto_added):
    now = meta["last_updated"]
    cards = []
    for p in providers:
        v = p.get("v_website", {"ok": False})
        status = status_badge(v)
        status_cls = v.get("state", "down")
        links = []
        for label, key, url in (("site", "v_website", p["website"]),
                                ("free", "v_free", p["free_url"]),
                                ("keys", "v_keys", p["key_url"]),
                                ("docs", "v_docs", p["docs_url"])):
            if p.get(key) and p[key]["ok"] and url:
                links.append(f'<a class="btn" href="{html_escape(url)}" target="_blank" rel="noopener">{label}</a>')
        if not links:
            links.append(f'<span class="btn dead">{status}</span>')
        badges = [
            f'<span class="badge api api-{api_slug(p)}">{compat_badge(p)}</span>',
            f'<span class="badge trust trust-{p["trust"]}">{p["trust"]}</span>',
        ]
        if p.get("discovered_at", "") == meta["last_updated"]:
            badges.insert(0, '<span class="badge fresh">NEW</span>')
        elif p.get("auto"):
            badges.insert(0, '<span class="badge auto">AUTO</span>')
        badges.append(f'<span class="badge status {status_cls}">{status}</span>')
        cc = "No credit card" if not p.get("credit_card_required", True) else "CC?"
        cards.append(f"""
<div class="card">
  <div class="card-top">
    <h3>{html_escape(p['name'])}</h3>
    <div class="badges">
      {''.join(badges)}
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
            f'<span class="dim">({html_escape(l["domain"])}, via {html_escape(l["source"])}, '
            f'score {l["score"]}: {html_escape(", ".join(l["hits"]))})</span></li>'
            for l in leads
        ) + "</ul>"

    src_html = "".join(f"<li>{html_escape(k)}: {html_escape(v)}</li>" for k, v in source_status.items())

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Free-LLM - Fresh Third-Party LLM API Offers</title>
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
.auto {{ background:#1a2433; color:#93c5fd; }}
.fresh {{ background:#0e3a2a; color:#34d399; }}
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
  <h1>Free-LLM <span>· fresh third-party LLM API offers</span></h1>
  <p class="sub">Auto-researched twice daily by a GitHub Actions bot. Last run: <strong>{now}</strong> ·
     {meta['ok_count']} providers OK · {meta['dead_count']} flagged ·
     {meta['auto_added_count']} auto-discovered this run ·
     <span class="badge fresh">NEW</span> = added this run · <span class="badge auto">AUTO</span> = auto-discovered earlier</p>
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
  Official big-name providers are excluded by design; focus is fresh third-party offers.
  Offers change fast - verify links before relying on anything.</footer>
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
    # CI-only guard: never run locally (keeps the local machine clean)
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
    blocklist = set(kb.get("_official_blocklist", []))
    news_domains = set(kb.get("_news_domains", []))
    print(f"[{now_iso}] loaded {len(providers)} third-party providers from knowledge base")

    # 2. Run web searches
    queries = [l.strip() for l in QUERIES_FILE.read_text(encoding="utf-8").splitlines()
               if l.strip() and not l.strip().startswith("#")]
    source_status = {}
    all_results = []

    def run_source(name, func, qs, max_n):
        ok = 0
        for q in qs[:max_n]:
            r = func(q)
            for item in r:
                item["_source"] = name
            all_results.extend(r)
            ok += 1 if r else 0
        source_status[name] = f"{ok}/{min(max_n, len(qs))} queries returned results"

    run_source("bing", search_bing, queries, MAX_BING_QUERIES)
    run_source("searxng", search_searxng, queries, MAX_SEARXNG_QUERIES)
    run_source("hackernews", search_hn, queries, MAX_HN_QUERIES)
    run_source("reddit", search_reddit_pullpush, queries, MAX_REDDIT_QUERIES)
    run_source("github", search_github, queries, MAX_GITHUB_QUERIES)
    run_source("google-news", search_google_news, queries, MAX_NEWS_QUERIES)
    run_source("x-twitter", search_nitter_x, queries, MAX_NITTER_QUERIES)

    # Telegram: channel scan (no query)
    tg = search_telegram(TELEGRAM_CHANNELS[:MAX_TELEGRAM_CHANNELS])
    for item in tg:
        item["_source"] = "telegram"
    all_results.extend(tg)
    source_status["telegram"] = f"{len(tg)} posts matched"

    # Lobsters: single fetch
    lob = search_lobsters()
    for item in lob:
        item["_source"] = "lobsters"
    all_results.extend(lob)
    source_status["lobsters"] = f"{len(lob)} newest stories scanned"

    print(f"[{now_iso}] search returned {len(all_results)} total results")

    # 3. Verify all tracked KB URLs in parallel
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

    # 4. Attach verification results
    for p in providers:
        p["v_website"] = verified.get(p.get("website"), {"ok": False, "status": "n/a", "state": "down", "url": p.get("website")})
        p["v_free"] = verified.get(p.get("free_url"), {"ok": False, "status": "n/a", "state": "down", "url": p.get("free_url")})
        p["v_keys"] = verified.get(p.get("key_url"), {"ok": False, "status": "n/a", "state": "down", "url": p.get("key_url")})
        p["v_docs"] = verified.get(p.get("docs_url"), {"ok": False, "status": "n/a", "state": "down", "url": p.get("docs_url")})
        p["verified_at"] = now_iso

    # 5. Leads
    known_domains = {domain_of(p.get("website", "")) for p in providers}
    leads = extract_leads(all_results, known_domains)
    print(f"[{now_iso}] {len(leads)} new leads")

    # 6. Auto-discover: assess top leads, auto-add authentic new providers
    auto_added = []
    for lead in leads[:MAX_AUTO_ADD_PER_RUN]:
        if len(providers) >= MAX_TOTAL_PROVIDERS:
            break
        a = assess_lead(lead, known_domains, blocklist, news_domains)
        if a and a["add"]:
            p = build_provider(lead, a, now_iso)
            p["v_website"] = {"ok": True, "status": a.get("status", 200), "state": "ok", "url": p["website"]}
            p["v_free"] = {"ok": True, "status": 200, "state": "ok", "url": p["free_url"]}
            p["v_keys"] = {"ok": False, "status": "n/a", "state": "down", "url": ""}
            p["v_docs"] = {"ok": False, "status": "n/a", "state": "down", "url": ""}
            p["verified_at"] = now_iso
            providers.append(p)
            known_domains.add(lead["domain"])
            auto_added.append({"name": p["name"], "domain": lead["domain"], "reasons": a["reasons"]})
    if auto_added:
        kb["providers"] = prune_providers(providers, verified)
        PROVIDERS_FILE.write_text(json.dumps(kb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[{now_iso}] AUTO-ADDED {len(auto_added)} providers: {[a['domain'] for a in auto_added]}")

    providers = prune_providers(providers, verified)

    ok_count = sum(1 for p in providers if p.get("v_website", {}).get("ok"))
    dead_count = len(providers) - ok_count
    auto_added_count = len(auto_added)

    meta = {
        "last_updated": now_iso,
        "providers_count": len(providers),
        "ok_count": ok_count,
        "dead_count": dead_count,
        "auto_added_count": auto_added_count,
        "leads_count": len(leads),
        "total_results": len(all_results),
        "sources": source_status,
    }

    # 7. Write outputs
    RESULTS_DIR.mkdir(exist_ok=True)
    SITE_DIR.mkdir(exist_ok=True)

    offers_payload = {
        "last_updated": now_iso,
        "summary": {k: meta[k] for k in ("ok_count", "dead_count", "auto_added_count", "leads_count", "total_results")},
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
                "credit_card_required": p.get("credit_card_required", True),
                "models": p["models"],
                "limits": p["limits"],
                "expiry": p["expiry"],
                "expiry_note": p.get("expiry_note", ""),
                "compat": p.get("compat", {}),
                "trust": p.get("trust", "unknown"),
                "notes": p.get("notes", ""),
                "auto": p.get("auto", False),
                "discovered_at": p.get("discovered_at", ""),
                "discovery_signals": p.get("discovery_signals", []),
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
        "auto_added": auto_added,
    }
    OFFERS_JSON.write_text(json.dumps(offers_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{now_iso}] wrote {OFFERS_JSON}")

    LEADS_JSON.write_text(
        json.dumps({"last_updated": now_iso, "count": len(leads), "leads": leads},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[{now_iso}] wrote {LEADS_JSON}")

    history_line = (f"- {now_iso} | providers={len(providers)} | ok={ok_count} | dead={dead_count} "
                    f"| auto-added={auto_added_count} | leads={len(leads)} | results={len(all_results)}\n")
    prev_history = HISTORY_MD.read_text(encoding="utf-8") if HISTORY_MD.exists() else ""
    prev_lines = prev_history.splitlines()[:90]
    HISTORY_MD.write_text(history_line + "\n".join(prev_lines) + ("\n" if prev_lines else ""), encoding="utf-8")

    md = render_markdown(providers, meta, leads, source_status, auto_added)
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

    SITE_HTML.write_text(render_html(providers, meta, leads, source_status, auto_added), encoding="utf-8")
    print(f"[{now_iso}] wrote {SITE_HTML}")

    print(f"[{now_iso}] DONE - summary: "
          f"{json.dumps({k: meta[k] for k in ('ok_count', 'dead_count', 'auto_added_count', 'leads_count', 'total_results')})}")


if __name__ == "__main__":
    main()
