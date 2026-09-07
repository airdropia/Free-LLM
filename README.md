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

## Latest Third-Party Offers - 2026-09-07T07:14:23Z

> 6 providers verified OK | 0 flagged | 1 auto-discovered this run | last full run: 2026-09-07T07:14:23Z


### ✨ Auto-discovered this run (new providers added)

- **blazephoenix.xyz** (`blazephoenix.xyz`) — mentions api, free/credit/trial signal, llm/model signal, homepage reachable (200)


| Provider | Client API | Models | Limits | Signup | Expiry | Links |
|---|---|---|---|---|---|---|
| **LLM7.io** (medium) | OPENAI-COMPAT | DeepSeek-R1; Qwen 2.5 | 30 RPM without signup; up to 5M tokens/day with free email token | no-CC none | ongoing | [site](https://llm7.io/) [free](https://llm7.io/) |
| **BazaarLink (free gateway)** (low) | OPENAI-COMPAT | Various via gateway (OpenAI-compatible) | Free OpenAI-compatible API key; model access varies | no-CC email | unknown | [site](https://bazaarlink.ai/free) [free](https://bazaarlink.ai/free) [keys](https://bazaarlink.ai/free) |
| **yolo-auto.com** ↻ (medium) | OPENAI-COMPAT | see website | Unmetered LLM API; paid plan reported ~$6/month, verify free tier | no-CC email | unknown | [site](https://yolo-auto.com) [free](https://yolo-auto.com) |
| **openlegion.ai** ↻ (medium) | OPENAI-COMPAT | see website | AI agent fleet with container isolation; free tier - verify | no-CC email | unknown | [site](https://openlegion.ai) [free](https://openlegion.ai) |
| **komilion.com** ↻ (medium) | OPENAI-COMPAT | see website | API router that picks the cheapest model for the task; free tier - verify | no-CC email | unknown | [site](https://komilion.com) [free](https://komilion.com) |
| **blazephoenix.xyz** ⚡ (medium) | OPENAI-COMPAT | see website | see website | no-CC email | unknown | [site](https://blazephoenix.xyz) [free](https://blazephoenix.xyz/) |

### New leads (unverified, found in today's search)

- [Free models you can use with your OpenClaw (no credit card needed)](https://news.ycombinator.com/item?id=47681837) (news.ycombinator.com, via hackernews, score 7: free, api key, credit, trial, new, key, api)

- [Unlimited AI Credits from One Integer: New API's Quota Overflow (CVE-2026-71479) and How to Check Your Gateway - Buttondown](https://news.google.com/rss/articles/CBMimgFBVV95cUxQZmhFb1p5UTMxb3Ryc2phRmZKOU81M1B3Um40MFA1YUFxRXM4NTh6VGhQa29PbUg2TnJoa3BlX0wwTEV5Zm9RcEZXNUc3YVdSVUNoaFVyT1J4bVVoTmVJQUJVTktjamMya2RvTjRSRUNTV25IaW13cGhfalNkSDVuZDZnRnhSMTBYbG1ObllzRWJ4QldSeXBPSDdn?oc=5) (news.google.com, via google-news, score 7: credits, credit, gateway, new, unlimited, limited, api)

- [Show HN: Faster more accurate multimodal vector search](https://github.com/nickswami/dasein-python-sdk) (github.com, via hackernews, score 6: free, api key, trial, week, key, api)

- [Show HN: Private AI assistant for $1.99 -Free AI](https://personalassistantdeploy.com/) (personalassistantdeploy.com, via hackernews, score 6: free, api key, api keys, month, key, api)

- [A DEX aggregator whose quotes are computed on-chain (free API, no key)](https://blazephoenix.xyz/) (blazephoenix.xyz, via hackernews, score 4: free, aggregator, key, api)

- [Show HN: One API for GPT-5, Claude-Sonnet-4, DeepSeek, Gemini](https://wisdom-gate.juheapi.com/studio/chat) (wisdom-gate.juheapi.com, via hackernews, score 3: aggregator, access, api)

- [Combining HTTP and JavaScript APIs with php](http://united-coders.com/christian-harms/combining-http-and-javascript-apis-with-php) (united-coders.com, via hackernews, score 3: free, aggregator, api)

- [Show HN: I made a free competition/giveaway aggregator](https://comps.gg) (comps.gg, via hackernews, score 3: free, giveaway, aggregator)

- [Show HN: Recase – A free proxy server to cache API calls for you](https://recase.herokuapp.com/landing/?next=/) (recase.herokuapp.com, via hackernews, score 3: free, proxy, api)

- [Show HN: Spidra – AI web scraper that adapts to any website](https://spidra.io) (spidra.io, via hackernews, score 3: new, launch, api)

- [Show HN: Pomo – Manage your Stripe promo codes without code](https://usecopi.com/69fb5996) (usecopi.com, via hackernews, score 3: free, promo, launch)

- [Show HN: LobsterLair – OpenClaw hosting with AI included ($19/mo)](https://lobsterlair.xyz) (lobsterlair.xyz, via hackernews, score 3: api key, key, api)

- [[TG:AI_Deals] Grab : Upto 85% Off on Aristocrat Trolleys + Bank Offers  😱    😱      🔗   Link:  https://www.amazon.in/s?hidden-keywords](https://www.amazon.in/s?hidden-keywords=B0H1MZV6FH%7CB0H2VRDNJK%7CB0H1MPQYKP%7CB0FC6RGJTT%7CB0FFBCLHTT&tag=aideals0ff-21) (amazon.in, via telegram, score 3: offer, deal, key)

- [NBC News - Breaking Headlines and Video Reports on World, U.S.](https://www.bing.com/ck/a?!&&p=cc3cd49d2f3736b7e13640c80f49d2ca99fcce52a82894b7789e9236496b1e9cJmltdHM9MTc4ODczOTIwMA&ptn=3&ver=2&hsh=4&fclid=27d6c06f-b0e4-6916-34c9-d7a2b1e86875&u=a1aHR0cHM6Ly93d3cubmJjbmV3cy5jb20v&ntb=1) (bing.com, via bing, score 2: new, week)

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

_Last verified: 2026-09-07T07:14:23Z. Offers change fast - verify links before relying on them._

<!-- OFFERS-END -->


