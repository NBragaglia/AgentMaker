# briefsmith-agent

`briefsmith-agent` converts messy `.txt` notes into a structured consulting/private equity work brief.

## Features

- Input validation with clear errors
- Modes: `internal`, `client`, `investment`
- Output sections in fixed order:
  - Situation
  - Key Findings
  - Risks
  - Open Questions
  - Next Steps
- Timestamped markdown output in `outputs/`
- Rule-based parsing with lightweight heuristics
- Unit tests with `pytest`

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
pip install pytest
```

## Run

```powershell
briefsmith-agent notes.txt --mode internal
briefsmith-agent .\data\deal_notes.txt --mode investment
briefsmith-agent client_call.txt --mode client --output-dir outputs
```

## Test

```powershell
pytest -q
```
