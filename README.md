# Free-LLM 🆓🤖

**Fresh third-party LLM API offers — auto-discovered twice daily, no credit card.**
Official big-name providers (Google, OpenAI, Anthropic, Groq, OpenRouter, Z.AI, Qwen, …)
are **excluded by design** — their generic free quotas can't finish a real coding task.
The bot hunts the **new routers / aggregators / gateways** that launch constantly,
including short-lived 1–2 week free offers for frontier models.

## 🔎 How it works (GitHub Actions, every 06:00 & 18:00 UTC)

1. **Aggressive search** across 9+ sources:
   - 🌐 **Bing** web search + **SearXNG** (multi-instance JSON)
   - 📰 **Google News RSS** — daily free-offer news
   - 🟠 **Hacker News** + 🔗 **Lobste.rs**
   - 🐦 **X/Twitter** (Nitter instances) + **Telegram** public channels
   - 🐙 **GitHub** repo search (newly launched providers)
   - 🔴 **Reddit** (pullpush.io archive — datacenter-friendly)
2. **Lead scoring** — every mention is keyword-scored (free / credits / trial / promo / giveaway / unlimited…).
3. **Auto-discovery** ✨ — top leads are assessed (site live? speaks API? free/credit signal? not an official provider?):
   - ✅ authentic → **auto-added to `bot/providers.json`** and committed back to the repo
4. **Daily link verification** — every tracked provider's links get `OK / BLOCKED / DEAD / DOWN` status.
5. **Auto-clean** — history capped at 90 entries, results fully regenerated each run, dead auto-added providers pruned.

## 📖 How to use the offers

1. Open the table below (or the [Pages site](https://airdropia.github.io/Free-LLM/)).
2. Pick a fresh provider — `⚡` = added this run, `↻` = auto-discovered earlier.
3. Click **keys** (or **site**), sign up with email, grab the API key.
4. Point your OpenAI-format client at their base URL + key.

**⚠️ Caution:** these are new, unproven third parties. `trust: low` gateways = unofficial
resellers — never send sensitive data, expect flakiness, always check the actual free tier
terms before building on it.

## 📁 Repo layout

| Path | Purpose |
|---|---|
| `bot/research.py` | The research bot (Python stdlib only, runs in GitHub Actions) |
| `bot/providers.json` | Third-party knowledge base + official-provider blocklist (bot auto-updates it) |
| `bot/queries.txt` | Daily search queries |
| `results/offers.json` | Latest structured results (machine-readable) |
| `results/leads.json` | Scored candidate leads from the latest run |
| `results/history.md` | Daily snapshot log (auto-capped) |
| `site/index.html` | GitHub Pages site (auto-generated) |

## 🚀 Manual run

**Actions → free-llm-daily-research → Run workflow** (or `gh workflow run research.yml`).

## 🧹 Self-cleaning

- Runs only inside GitHub Actions — never touches the local machine.
- `results/` + `site/` regenerated every run; history capped; dead auto-providers pruned;
  old Pages artifacts expire automatically.

## ⚠️ Disclaimer

Free tiers change fast; links are re-verified daily but nothing here is a guarantee.
Auto-discovered providers are community finds, not endorsements.

---

## 📊 Latest Third-Party Offers








<!-- OFFERS-START -->

## Latest Third-Party Offers - 2026-09-09T10:45:48Z

> 7 providers verified OK | 0 flagged | 0 auto-discovered this run | last full run: 2026-09-09T10:45:48Z


| Provider | Client API | Models | Limits | Signup | Expiry | Links |
|---|---|---|---|---|---|---|
| **LLM7.io** (medium) | OPENAI-COMPAT | DeepSeek-R1; Qwen 2.5 | 30 RPM without signup; up to 5M tokens/day with free email token | no-CC none | ongoing | [site](https://llm7.io/) [free](https://llm7.io/) |
| **BazaarLink (free gateway)** (low) | OPENAI-COMPAT | Various via gateway (OpenAI-compatible) | Free OpenAI-compatible API key; model access varies | no-CC email | unknown | [site](https://bazaarlink.ai/free) [free](https://bazaarlink.ai/free) [keys](https://bazaarlink.ai/free) |
| **yolo-auto.com** ↻ (medium) | OPENAI-COMPAT | see website | Unmetered LLM API; paid plan reported ~$6/month, verify free tier | no-CC email | unknown | [site](https://yolo-auto.com) [free](https://yolo-auto.com) |
| **openlegion.ai** ↻ (medium) | OPENAI-COMPAT | see website | AI agent fleet with container isolation; free tier - verify | no-CC email | unknown | [site](https://openlegion.ai) [free](https://openlegion.ai) |
| **komilion.com** ↻ (medium) | OPENAI-COMPAT | see website | API router that picks the cheapest model for the task; free tier - verify | no-CC email | unknown | [site](https://komilion.com) [free](https://komilion.com) |
| **blazephoenix.xyz** ↻ (medium) | OPENAI-COMPAT | see website | see website | no-CC email | unknown | [site](https://blazephoenix.xyz) [free](https://blazephoenix.xyz/) |
| **Download A Free PC Game Every Week - Epic Games Store** ↻ (medium) | OPENAI-COMPAT | see website | see website | no-CC email | unknown | [site](https://bing.com) [free](https://www.bing.com/ck/a?!&&p=ecbb143ce464506739ea732064ece0cd7ed0a7f109e378f470e50e8c7dab3fa9JmltdHM9MTc4ODgyNTYwMA&ptn=3&ver=2&hsh=4&fclid=264e8efd-936e-6193-2c1e-993392fa605a&u=a1aHR0cHM6Ly9zdG9yZS5lcGljZ2FtZXMuY29tL2ZyZWUtZ2FtZXM_bGFuZz1lbi1VUw&ntb=1) |

### New leads (unverified, found in today's search)

- [Free models you can use with your OpenClaw (no credit card needed)](https://news.ycombinator.com/item?id=47681837) (news.ycombinator.com, via hackernews, score 7: free, api key, credit, trial, new, key, api)

- [Show HN: Faster more accurate multimodal vector search](https://github.com/nickswami/dasein-python-sdk) (github.com, via hackernews, score 6: free, api key, trial, week, key, api)

- [Show HN: Private AI assistant for $1.99 -Free AI](https://personalassistantdeploy.com/) (personalassistantdeploy.com, via hackernews, score 6: free, api key, api keys, month, key, api)

- [Google and OpenAI offer free API credits—but there's one catch - How-To Geek](https://news.google.com/rss/articles/CBMikAFBVV95cUxQTEttNldEemZuTHJ3clRMblBLYWVobl9MZnN5NzRUMnAxOTZaYWZPVUZRcUxNZl96TnN3ekZ4T05UZWUyQXlWdE5YbVBQblRHcWp5SEF2VURra0EwZkRIbG1Od21KWGdMU0lkRHk2WXRhdHJuZ1NHTWlWaklRSFh0RGRDd1Z0MHMzS0xYWVQyYXE?oc=5) (news.google.com, via google-news, score 6: free, credits, credit, offer, new, api)

- [Show HN: One API for GPT-5, Claude-Sonnet-4, DeepSeek, Gemini](https://wisdom-gate.juheapi.com/studio/chat) (wisdom-gate.juheapi.com, via hackernews, score 3: aggregator, access, api)

- [Combining HTTP and JavaScript APIs with php](http://united-coders.com/christian-harms/combining-http-and-javascript-apis-with-php) (united-coders.com, via hackernews, score 3: free, aggregator, api)

- [Show HN: I made a free competition/giveaway aggregator](https://comps.gg) (comps.gg, via hackernews, score 3: free, giveaway, aggregator)

- [Show HN: Recase – A free proxy server to cache API calls for you](https://recase.herokuapp.com/landing/?next=/) (recase.herokuapp.com, via hackernews, score 3: free, proxy, api)

- [Show HN: Spidra – AI web scraper that adapts to any website](https://spidra.io) (spidra.io, via hackernews, score 3: new, launch, api)

- [Show HN: Pomo – Manage your Stripe promo codes without code](https://usecopi.com/69fb5996) (usecopi.com, via hackernews, score 3: free, promo, launch)

- [Show HN: LobsterLair – OpenClaw hosting with AI included ($19/mo)](https://lobsterlair.xyz) (lobsterlair.xyz, via hackernews, score 3: api key, key, api)

- [[TG:AI_Deals] Grab : Upto 85% Off on Aristocrat Trolleys + Bank Offers  😱    😱      🔗   Link:  https://www.amazon.in/s?hidden-keywords](https://www.amazon.in/s?hidden-keywords=B0H1MZV6FH%7CB0H2VRDNJK%7CB0H1MPQYKP%7CB0FC6RGJTT%7CB0FFBCLHTT&tag=aideals0ff-21) (amazon.in, via telegram, score 3: offer, deal, key)

- [Launch HN: Speko (YC S26) – OpenRouter for Voice AI](https://speko.ai/) (speko.ai, via hackernews, score 2: router, launch)

- [Show HN: LaunchPad – Job aggregator I built overnight after Amazon layoffs](https://launchpad-kappa-ashy.vercel.app/) (launchpad-kappa-ashy.vercel.app, via hackernews, score 2: aggregator, launch)

- [Show HN: Smplogs – Local-first AWS Cloudwatch log analyzer via WASM](https://www.smplogs.com) (smplogs.com, via hackernews, score 2: gateway, api)

- [Show HN: AI coding agent for VS Code with pay-as-you-go pricing- no subscription](https://www.llmonestop.com/#pricing) (llmonestop.com, via hackernews, score 2: month, key)

- [Show HN: Get GPT-5.2, Grok-4.1-fast, KimiK2.5 and more LLMs at half the cost](https://frogapi.app) (frogapi.app, via hackernews, score 2: gateway, api)

- [Show HN: Till.sh, enhanced access controls for AWS S3](https://till.sh) (till.sh, via hackernews, score 2: access, month)

- [Show HN: Zodii – a developer-first astrology, numerology and tarot API platform](https://www.zodiiapp.com/) (zodiiapp.com, via hackernews, score 2: free, api)

- [Show HN: Twogether AI – Multi-Person Photo Generation API](https://twogether.ai/?source=hn) (twogether.ai, via hackernews, score 2: launch, api)

- [Show HN: Gensee – Free AI Agent Optimization and Deployment](https://platform.gensee.ai) (platform.gensee.ai, via hackernews, score 2: free, launch)

- [Show HN: Quiltt Connector, Embeddable onboarding for finance products](https://www.quiltt.io/product/connector) (quiltt.io, via hackernews, score 2: new, launch)

- [Show HN: Run any Llama model finetune and more, instantly](https://featherless.ai) (featherless.ai, via hackernews, score 2: new, api)

- [Show HN: SanctionSnap – free 250 sanctions checks via API](https://sanctionsnap.com) (sanctionsnap.com, via hackernews, score 2: free, api)

- [Show HN: Gradient – a web API for fine-tuning and deploying Llama2](https://gradient.ai/) (gradient.ai, via hackernews, score 2: launch, api)

- [[TG:AI_Deals] MediBuddy Loot : Flat ₹5151 Off on Full Body Health Check-Up + FREE Vitamin Tests   🔥    🔥      👉   63+ Lab Tests (Vitam](https://bilty.co/ydk1PE) (bilty.co, via telegram, score 2: free, deal)

### Source status

- bing: 12/12 queries returned results
- searxng: 0/8 queries returned results
- hackernews: 14/14 queries returned results
- reddit: 0/5 queries returned results
- github: 5/5 queries returned results
- google-news: 8/8 queries returned results
- x-twitter: 0/2 queries returned results
- telegram: 3 posts matched
- lobsters: 25 newest stories scanned

_Last verified: 2026-09-09T10:45:48Z. Offers change fast - verify links before relying on them._

<!-- OFFERS-END -->







