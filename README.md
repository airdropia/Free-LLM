# Free-LLM 🆓🤖

**Daily-researched directory of free LLM API offers — no credit card, just email/Google/GitHub signups.**
Every offer is tagged with the API type it speaks (`OPENAI-COMPAT` works with any OpenAI-format client).

A GitHub Actions bot re-runs research **every day (06:00 UTC)**:

1. **Verifies** every provider link in the curated knowledge base (`bot/providers.json`) — dead links get flagged (`OK` / `BLOCKED` / `DEAD` / `DOWN`).
2. **Searches the web** (DuckDuckGo + Hacker News + Reddit + GitHub) for new free-LLM-offer signals.
3. **Discovers new leads** — unknown domains surfacing in today's results.
4. **Commits** results to this repo and **deploys** the GitHub Pages site.

## 📖 How to use the offers

1. Pick a provider from the table below. Prefer `OPENAI-COMPAT` offers — they work with any OpenAI-format client.
2. Click its **keys** link, sign up (email/Google/GitHub, no credit card), generate an API key.
3. Point your client at the provider's base URL + key. Most providers are drop-in OpenAI-compatible:

```bash
export OPENAI_BASE_URL="https://api.groq.com/openai/v1"   # example: Groq
export OPENAI_API_KEY="<your key from console.groq.com/keys>"
```

Not OpenAI-compatible (e.g. `GOOGLE API`, `COHERE`) means the provider has its own SDK/format — still usable, just not with generic OpenAI clients.

## 📁 Repo layout

| Path | Purpose |
|---|---|
| `bot/research.py` | The research bot (Python stdlib only, runs in GitHub Actions) |
| `bot/providers.json` | Curated knowledge base — edit to add/update providers |
| `bot/queries.txt` | Daily search queries (DuckDuckGo / Hacker News) |
| `results/offers.json` | Latest structured results (machine-readable) |
| `results/history.md` | Daily snapshot log (auto-capped at 90 entries) |
| `site/index.html` | GitHub Pages site (auto-generated) |

## 🚀 Manual run

Trigger a fresh research run any time: **Actions → free-llm-daily-research → Run workflow**
(or `gh workflow run research.yml`).

## 🧹 Self-cleaning

- Runs only inside GitHub Actions — never touches the local machine.
- `results/` and `site/` are fully regenerated every run (no stale files).
- History log is capped; old Pages artifacts expire automatically.

## ⚠️ Disclaimer

Free tiers change frequently (limits, model availability, signup requirements).
Links are re-verified daily but nothing here is a guarantee — always confirm on
the provider's own site before relying on an offer. Providers marked `trust: low`
are unofficial gateways — use at your own risk, never send sensitive data.

---

## 📊 Latest Offers

<!-- OFFERS-START -->

_First run in progress — results appear here after the bot's first execution._

<!-- OFFERS-END -->
