# AgentMaker

Monorepo for building and storing multiple AI agents in separate folders.

## Structure

```text
AgentMaker/
  agents/                    # Each built agent lives here
  templates/                 # Reusable starter templates
    python-cli-agent/        # Default Python CLI agent starter
  shared/                    # Shared scripts/docs/snippets across agents
  scripts/
    new-agent.ps1            # Scaffold a new agent from a template
  docs/
    COST_SAFETY.md           # No-surprise-cost policy and checklist
```

## Quick Start

1. Create a new agent from template:

```powershell
./scripts/new-agent.ps1 -Name briefsmith-v2
```

2. Agent folder is created at:

```text
agents/briefsmith-v2
```

3. Follow the generated `README.md` inside that folder.

## Cost Safety (High Priority)

- Default workflow uses local files + Codex CLI with ChatGPT login.
- Do **not** set `OPENAI_API_KEY` unless you intentionally want API billing.
- Use `codex login status` and keep auth as `Logged in using ChatGPT`.
- Before running any cloud/deploy command, run through `docs/COST_SAFETY.md`.

## Notes

- GitHub repo is public (`NBragaglia/AgentMaker`), which helps avoid paid private-repo CI costs.
- If any task might incur billing, we will pause and ask for explicit approval first.
