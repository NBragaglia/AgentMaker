# stock-master

`stock-master` is a practical starter package for building a production-oriented stock analysis and portfolio intelligence agent.

It now includes:
1. A richer **system prompt blueprint** (`AGENT_PROMPT.md`) you can paste directly into Codex/LLM workflows.
2. A small CLI utility that helps you quickly **inspect the prompt**, **generate an implementation brief**, and **bootstrap all planning artifacts**.

## Included assets

- `AGENT_PROMPT.md` — canonical long-form specification prompt.
- `src/stock_master/prompt_assets.py` — packaged prompt + implementation brief + constraints questionnaire templates.
- `src/stock_master/cli.py` — CLI entrypoint with practical commands.
- `tests/test_cli.py` — unit tests for CLI flows and edge cases.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
pip install pytest
```

## CLI usage

### 1) Inspect installed prompt

```bash
stock-master show-prompt
```

### 2) Generate only the implementation brief

```bash
stock-master init-brief
```

### 3) Bootstrap the full planning pack (recommended)

```bash
stock-master bootstrap --output-dir work/stock-master
```

This creates:

```text
work/stock-master/AGENT_PROMPT.md
work/stock-master/stock_master_implementation_brief.md
work/stock-master/stock_master_constraints.json
```

### 4) Overwrite an existing planning pack

```bash
stock-master bootstrap --output-dir work/stock-master --force
```

## Suggested run sequence (10 minutes)

1. Create the planning pack with `bootstrap`.
2. Fill `stock_master_constraints.json` with your real market/horizon/budget/broker details.
3. Paste `AGENT_PROMPT.md` into your LLM and include your filled constraints.
4. Use generated outputs to refine `stock_master_implementation_brief.md` into concrete tickets.

## Test

```bash
PYTHONPATH=src pytest -q tests
```
