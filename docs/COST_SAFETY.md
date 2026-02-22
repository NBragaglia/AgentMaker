# No-Surprise-Cost Policy

Date: 2026-02-22

Goal: Keep development on free/local tooling unless you explicitly approve a paid step.

## Defaults to Keep

1. Use Codex CLI with ChatGPT login, not API key billing.
2. Keep repos public when possible.
3. Prefer local execution over hosted services.
4. Do not enable paid cloud deploy targets by default.

## Hard Rules

1. Never run a command that could create paid cloud resources without explicit approval.
2. Never add paid API keys to scripts/config by default.
3. Call out any command with potential billing impact before running it.

## Safe Check Commands

```powershell
codex login status
$env:OPENAI_API_KEY
$env:ANTHROPIC_API_KEY
$env:AZURE_OPENAI_API_KEY
```

Expected for cost safety:
- `codex login status` says `Logged in using ChatGPT`
- API key env vars are empty unless intentionally configured

## Known Caveat

ChatGPT Plus has product usage limits. Exceeding limits can block usage, and optional upgrades may cost money. We avoid optional paid paths unless you approve them.
