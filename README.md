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

_First run in progress — results appear here after the bot's next execution._

<!-- OFFERS-END -->
