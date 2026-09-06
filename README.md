# Free-LLM 🆓🤖

**Daily-researched directory of free LLM API offers — no credit card, just email/Google/GitHub signups.**
Every offer is tagged with the API type it speaks (`OPENAI-COMPAT` works with any OpenAI-format client).

A GitHub Actions bot re-runs research **twice daily (06:00 & 18:00 UTC)** across **10 sources**:

- 🌐 **DuckDuckGo** web search (16 queries)
- 📰 **Google News RSS** — daily free-offer news
- 🟦 **Bluesky** public API — real-time chatter
- 🐦 **X/Twitter** via Nitter instances
- 🔗 **Lobste.rs** tech community
- 🐙 **GitHub** repo search — newly launched providers
- 🟠 **Hacker News** + **Reddit**

Each run:

1. **Verifies** every provider link in the curated knowledge base (`bot/providers.json`) — dead links get flagged (`OK` / `BLOCKED` / `DEAD` / `DOWN`).
2. **Aggressively searches** all sources for new free-LLM-offer signals (including short-lived 1-2 week frontier-model offers).
3. **Scores new leads** by keyword relevance → `results/leads.json`.
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
| `results/leads.json` | Scored new-lead candidates discovered in the latest run |
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

## Latest Offers - 2026-09-06T19:10:59Z

> 22 providers verified OK | 3 flagged | 23 client-ready (OpenAI-compatible or native API) | last full run: 2026-09-06T19:10:59Z

| Provider | Client API | Models | Limits | Signup | Expiry | Links |
|---|---|---|---|---|---|---|
| **Google AI Studio (Gemini)** (high) | GOOGLE API | Gemini 3.1 Pro; Gemini 3.1 Flash; Gemini 3.0 Flash; Gemini 3.0 Flash-Lite | Free tier: 5-30 RPM depending on model; ~9,000 requests/day on Flash; 25 RPD on Pro; 1M token context available | no-CC google | ongoing | [site](https://aistudio.google.com/) [free](https://ai.google.dev/gemini-api/docs/rate-limits) [keys](https://aistudio.google.com/apikey) [docs](https://ai.google.dev/gemini-api/docs) |
| **Groq** (high) | OPENAI-COMPAT | Llama 3.3 70B Versatile; Llama 3.1 8B; Qwen 2.5 Coder 32B; Whisper Large v3 | Free tier: 30 RPM, 14,400 requests/day. Very high token throughput (~320 tok/s on 70B) | no-CC email | ongoing | [site](https://groq.com/) [free](https://console.groq.com/) [keys](https://console.groq.com/keys) [docs](https://console.groq.com/docs) |
| **OpenRouter** (high) | OPENAI-COMPAT | 100+ free models with ':free' suffix; DeepSeek V3/R1; Qwen; Llama … | Free models: 20 RPM, 50 requests/day (1,000/day after $10 top-up). One key routes across many providers | no-CC email | ongoing | [site](https://openrouter.ai/) [free](https://openrouter.ai/models?max_price=0) [keys](https://openrouter.ai/settings/keys) [docs](https://openrouter.ai/docs) |
| **Cloudflare Workers AI** (high) | OPENAI-COMPAT | Llama 3.1 8B Instruct; Llama 3.2 3B Instruct; Mistral 7B Instruct; Qwen 1.5 7B Chat … | Free plan: 10,000 neurons/day (~300,000 neurons/month) | no-CC email | ongoing | [site](https://developers.cloudflare.com/workers-ai/) [free](https://developers.cloudflare.com/workers-ai/platform/pricing/) [docs](https://developers.cloudflare.com/workers-ai/) |
| **Mistral (La Plateforme)** (high) | OPENAI-COMPAT | Mistral Small 3; Mistral Nemo; Mistral 7B; Codestral (Experiment tier) | Experiment free tier: ~1B tokens/month on Codestral; ~1 request/second; requires opt-in to training | no-CC email | ongoing | [site](https://mistral.ai/) [free](https://console.mistral.ai/) [keys](https://console.mistral.ai/api-keys) [docs](https://docs.mistral.ai/) |
| **Cerebras** (high) | OPENAI-COMPAT | Llama 3.3 70B; Llama 3.1 8B; DeepSeek R1 Distill | Free tier: ~1M tokens/day, ~30 RPM. Extremely fast inference | no-CC email | ongoing | [site](https://www.cerebras.ai/) [free](https://www.cerebras.ai/pricing) [keys](https://cloud.cerebras.ai/) [docs](https://inference-docs.cerebras.ai/) |
| **NVIDIA NIM** (high) | OPENAI-COMPAT | 120+ open-weight models; DeepSeek R1; Llama 3.3 70B; Qwen 2.5 Coder … | Free API credits for developers; ~40 RPM; OpenAI-compatible endpoint | no-CC email | ongoing | [site](https://build.nvidia.com/) [free](https://build.nvidia.com/) [keys](https://org.ngc.nvidia.com/setup/api-key) [docs](https://docs.api.nvidia.com/nim/reference/getting-started) |
| **Hugging Face Inference Providers** (high) | OPENAI-COMPAT | Llama 3.2 11B Vision; Llama 3.1 8B Instruct; Qwen 2.5 72B Instruct; Gemma 2 9B … | Free routing credits ~$0.10/month; 300 requests/hour cap | no-CC email | ongoing | [keys](https://huggingface.co/settings/tokens) [docs](https://huggingface.co/docs/inference-providers/index) |
| **Cohere** (high) | COHERE | Command R+; Command R; Command A (111B) | Trial key: ~20 RPM, 1,000 requests/month; non-commercial use | no-CC email | ongoing | [site](https://cohere.com/) [free](https://docs.cohere.com/docs/rate-limits) [keys](https://dashboard.cohere.com/api-keys) [docs](https://docs.cohere.com/) |
| **Z.AI (Zhipu GLM)** (high) | OPENAI-COMPAT | GLM-4.5-Flash; GLM-4.7-Flash; GLM-4.5 Air | Free Flash tier: ~1 request/second, ~1,000 requests/day | no-CC email | ongoing | [site](https://z.ai/) [free](https://open.bigmodel.cn/) [keys](https://open.bigmodel.cn/usercenter/apikeys) [docs](https://docs.z.ai/) |
| **GitHub Models** (high) | OPENAI-COMPAT | GPT-4o; GPT-4.1; Claude 3.5/3.7 Sonnet; Llama 3.3 … | Free tier: 15 RPM, 150-1,000 requests/day depending on model; Azure OpenAI-compatible endpoint | no-CC github | ongoing | [site](https://github.com/marketplace/models) [free](https://github.com/marketplace/models) [keys](https://github.com/settings/tokens) [docs](https://docs.github.com/en/github-models) |
| **DeepSeek** (high) | OPENAI-COMPAT | DeepSeek-V3.2; DeepSeek-R1 | ~10M token trial for new accounts; thereafter extremely low pay-as-you-go pricing | no-CC email | trial | [docs](https://api-docs.deepseek.com/) |
| **xAI (Grok)** (high) | OPENAI-COMPAT | Grok 3; Grok 3 Fast; Grok 4 | Free tier for new accounts: ~5M tokens on signup (valid ~30 days); generous rate limits while it lasts | no-CC email | trial | [docs](https://docs.x.ai/) |
| **Fireworks AI** (high) | OPENAI-COMPAT | Llama 3.3 70B; Mixtral 8x7B; Qwen 2.5; DeepSeek R1 | $1 free credit for new accounts; some models free tier | no-CC email | trial | [site](https://fireworks.ai/) [free](https://fireworks.ai/pricing) [docs](https://docs.fireworks.ai/) |
| **Together AI** (high) | OPENAI-COMPAT | Llama 3.3 70B; DeepSeek R1; Qwen 2.5 Coder; GLM-4 | Free signup credit (reported $1-$25 depending on period); pay-as-you-go after | no-CC email | trial | [site](https://www.together.ai/) [free](https://www.together.ai/pricing) [keys](https://api.together.ai/settings/api-keys) [docs](https://docs.together.ai/) |
| **Baseten** (high) | OPENAI-COMPAT | Llama 3.1; Mixtral; Qwen 2.5 | $30 free credit; card required once credit exhausted | **CC** email | trial | [site](https://www.baseten.co/) [free](https://www.baseten.co/pricing/) [keys](https://app.baseten.co/) [docs](https://docs.baseten.co/) |
| **SambaNova Cloud** (high) | OPENAI-COMPAT | Llama 3.1 405B; Llama 3.3 70B; DeepSeek R1 | $5 free credit; credit card required at signup | **CC** email | trial | [site](https://cloud.sambanova.ai/) [free](https://cloud.sambanova.ai/) [keys](https://cloud.sambanova.ai/apis) [docs](https://docs.sambanova.ai/) |
| **Coze (ByteDance)** (medium) | OTHER | GPT-4o (via Coze); Gemini 1.5 Pro (via Coze); Doubao; Kimi | Token-based daily quotas, reset daily; no card | no-CC email | ongoing | [site](https://www.coze.com/) [free](https://www.coze.com/home) [keys](https://www.coze.com/home) [docs](https://www.coze.com/docs) |
| **Nebius AI Studio** (medium) | OPENAI-COMPAT | Llama 3.3 70B; Qwen 2.5 Coder 32B; DeepSeek R1 | $1 free credit | no-CC email | trial | [site](https://studio.nebius.ai/) [free](https://studio.nebius.ai/) [keys](https://studio.nebius.ai/settings/api-keys) [docs](https://docs.nebius.com/) |
| **AI21 (Jamba)** (medium) | OPENAI-COMPAT | Jamba 1.5; Jamba 1.5 Mini; Jamba 1.5 Large | $10 trial credit | no-CC email | trial | [site](https://www.ai21.com/) [free](https://www.ai21.com/studio) [keys](https://studio.ai21.com/) [docs](https://docs.ai21.com/) |
| **Moonshot AI (Kimi)** (high) | OPENAI-COMPAT | Kimi K2; Kimi K2.5; moonshot-v1-32k | Free tier with limited daily tokens for new accounts (China phone required for full quota) | no-CC email | trial | [site](https://platform.moonshot.ai/) [free](https://platform.moonshot.ai/) [docs](https://platform.moonshot.ai/docs) |
| **MiniMax** (high) | OPENAI-COMPAT | MiniMax M2; MiniMax M1; MiniMax Text-01 | Free tier for new accounts with daily token quota | no-CC email | trial | [site](https://www.minimax.io/) [free](https://platform.minimaxi.com/) [keys](https://platform.minimaxi.com/user-center/basic-information/interface-key) |
| **Alibaba Cloud Model Studio (Qwen)** (high) | OPENAI-COMPAT | Qwen2.5-Max; Qwen2.5-Coder-32B; Qwen3 | New users get free quota (tokens) for Qwen models; China/Global dashboards differ | no-CC email | trial | [site](https://www.alibabacloud.com/en/product/modelstudio) [free](https://dashscope.console.aliyun.com/) [keys](https://dashscope.console.aliyun.com/apiKey) [docs](https://www.alibabacloud.com/help/en/model-studio/) |
| **BazaarLink (free gateway)** (low) | OPENAI-COMPAT | Various via gateway (OpenAI-compatible) | Free OpenAI-compatible API key; model access varies | no-CC email | unknown | [site](https://bazaarlink.ai/free) [free](https://bazaarlink.ai/free) [keys](https://bazaarlink.ai/free) |
| **LLM7.io** (medium) | OPENAI-COMPAT | DeepSeek-R1; Qwen 2.5 | 30 RPM without signup; up to 5M tokens/day with free email token | no-CC none | ongoing | [site](https://llm7.io/) [free](https://llm7.io/) |

### New leads (unverified, found in today's search)

- [A free web-based AI chat tool leveraging Puter](https://news.ycombinator.com/item?id=45710013) (news.ycombinator.com, via hackernews, score 8: free, gpt, claude, gemini, qwen, deepseek, new, deal)
- [Show HN: One API for GPT-5, Claude-Sonnet-4, DeepSeek, Gemini](https://wisdom-gate.juheapi.com/studio/chat) (wisdom-gate.juheapi.com, via hackernews, score 6: gpt, claude, gemini, deepseek, sonnet, access)
- [Show HN: An unmetered LLM API–$6/month, no token tracking, no limits](https://yolo-auto.com/) (yolo-auto.com, via hackernews, score 6: credits, credit, frontier, gpt, claude, month)
- [X offers free API credits for its Grok Bot - Social Media Today](https://news.google.com/rss/articles/CBMikgFBVV95cUxPZTlRU0pPb2czSEprX0lKNFM5S1N3Ujl4bVRPT0s2LTdGTkhFZlBwYUNndXliQU9FSWFJZHhFcjJuM2pvcUZVOXdWNURodlRQX2dOUjJ1MEw3dkxjclMxNVFRX1l6X0MwZUFfYU9ZY29VTDdQX0xUNWlWSEp5MlhVSUQ2RmZTekE1WlFGREJiSkloQQ?oc=5) (news.google.com, via google-news, score 6: free, credits, credit, offer, grok, new)
- [Show HN: Chat with Orion – a visual agent that sees, reasons and acts](https://chat.vlm.run/) (chat.vlm.run, via hackernews, score 5: frontier, gpt, claude, gemini, new)
- [Show HN: Generous free tier for SERP and AI web scraping](https://cloro.dev/) (cloro.dev, via hackernews, score 5: free, gpt, gemini, grok, new)
- [Show HN: LLM Onestop – Access ChatGPT, Claude, Gemini, and more in one interface](https://www.llmonestop.com) (llmonestop.com, via hackernews, score 4: gpt, claude, gemini, access)
- [Show HN: AudioWorkletProcessor Generator Powered by AI](https://angular-audio.com/worklet-generator) (angular-audio.com, via hackernews, score 4: free, credits, credit, signup)
- [Show HN: Dereference.dev – Prompt-First IDE for Parallel Claude Code Sessions](https://www.dereference.dev/) (dereference.dev, via hackernews, score 4: claude, access, new, month)
- [Show HN: Get GPT-5.2, Grok-4.1-fast, KimiK2.5 and more LLMs at half the cost](https://frogapi.app) (frogapi.app, via hackernews, score 4: gpt, grok, kimi, gateway)
- [Show HN: Onera – end-to-end encrypted AI chat](https://onera.chat) (onera.chat, via hackernews, score 3: api key, api keys, access)
- [Show HN: LibreThinker, free AI assistant for LibreOffice Writer, 10k installs](https://librethinker.com/) (librethinker.com, via hackernews, score 3: free, new, month)
- [Show HN: I Built Zero-Knowledge .env Sharing](https://secretdrop.dev/) (secretdrop.dev, via hackernews, score 3: api key, api keys, week)
- [Show HN: Vlm Run, Extract JSON from images, videos and documents in a simple API](https://vlm.run/) (vlm.run, via hackernews, score 3: gpt, gemini, month)
- [A developer exploited an API flaw to provide free access to GPT-4](https://techcrunch.com/2023/04/25/a-developer-exploited-an-api-flaw-to-provide-free-access-to-gpt-4/) (techcrunch.com, via hackernews, score 3: free, gpt, access)
- [Show HN: GPT UI similar to ChatGPT but with sudo access](https://chat.lit.codes/) (chat.lit.codes, via hackernews, score 3: api key, gpt, access)
- [Show HN: Llmswap v3.0 – CLI and SDK for OpenAI, Claude, Gemini, Watsonx](https://pypi.org/project/llmswap/) (pypi.org, via hackernews, score 3: claude, gemini, llama)
- [Launch HN: Speko (YC S26) – OpenRouter for Voice AI](https://speko.ai/) (speko.ai, via hackernews, score 3: openrouter, router, launch)
- [Show HN: Pomo – Manage your Stripe promo codes without code](https://usecopi.com/69fb5996) (usecopi.com, via hackernews, score 3: free, promo, launch)
- [Show HN: Ctxsync – Chat with your codebase that stays in sync](https://ctxsync.com) (ctxsync.com, via hackernews, score 2: gpt, week)
- [Show HN: NCompass Technologies – yet another AI Inference API, but hear us out](https://www.ncompass.tech/about) (ncompass.tech, via hackernews, score 2: access, new)
- [Show HN: Stateful AI API with OS Models](https://ark-labs.com/) (ark-labs.com, via hackernews, score 2: tokens, launch)
- [Show HN: Handelsregister.ai – Dev-friendly API for the German business registry](https://handelsregister.ai/de) (handelsregister.ai, via hackernews, score 2: access, register)
- [Show HN: Vxpix – $50 Lifetime Screenshot API, Free Tier with No Signup](https://tool.vxpix.com/) (tool.vxpix.com, via hackernews, score 2: free, signup)
- [Show HN: JSONBin – Free JSON storage API (no signup required)](https://jsonbin-zeta.vercel.app) (jsonbin-zeta.vercel.app, via hackernews, score 2: free, signup)
- [Show HN: RouterLab – open-source AI API with Swiss hosting](https://routerlab.ch) (routerlab.ch, via hackernews, score 2: router, access)
- [Show HN: Command-G – Copilot for Xcode made possible using Mac Accessibility API](https://www.commandg.app/) (commandg.app, via hackernews, score 2: gpt, access)
- [Show HN: AI Image Describer – GPT-4o Vision for alt text and SEO descriptions](https://ai-image-describer.online/) (ai-image-describer.online, via hackernews, score 2: gpt, access)
- [Show HN: Jobbi – Free AI resume tailoring with unlimited PDF exports](https://jobbi.app) (jobbi.app, via hackernews, score 2: free, limited)
- [Show HN: OPC Skills – 9 AI agent skills for solopreneurs (Claude Code, Cursor)](https://opc.dev/) (opc.dev, via hackernews, score 2: promo, claude)
- [Free LLM API – every free model behind one key](https://freellmapi.co/) (freellmapi.co, via hackernews, score 1: free)
- [Show HN: SkillScan – Free API to detect malicious AI agent skill files](https://skillscan.chitacloud.dev) (skillscan.chitacloud.dev, via hackernews, score 1: free)
- [Show HN: LobsterLair – OpenClaw hosting with AI included ($19/mo)](https://lobsterlair.xyz) (lobsterlair.xyz, via hackernews, score 1: api key)
- [Show HN: Finqual – Free SEC-based API for fundamentals, insider and 13F data](https://finqual.app/) (finqual.app, via hackernews, score 1: free)
- [Show HN: Zodii – a developer-first astrology, numerology and tarot API platform](https://www.zodiiapp.com/) (zodiiapp.com, via hackernews, score 1: free)
- [Show HN: SharpAPI – Real-time sports odds API with +EV and arbitrage detection](https://sharpapi.io) (sharpapi.io, via hackernews, score 1: free)
- [Show HN: Free API mock server from your OpenAPI spec (no sign-up)](https://apinotes.io/mock-server) (apinotes.io, via hackernews, score 1: free)

### Source status

- duckduckgo: 0/16 queries returned results
- hackernews: 13/14 queries returned results
- reddit: 0/4 queries returned results
- github: 5/5 queries returned results
- google-news: 8/8 queries returned results
- bluesky: 0/8 queries returned results
- x-twitter: 0/2 queries returned results
- lobsters: 25 newest stories scanned

_Last verified: 2026-09-06T19:10:59Z. Free tiers change often - check links before relying on them._

<!-- OFFERS-END -->


