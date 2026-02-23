# briefsmith-agent

`briefsmith-agent` converts messy `.txt` or `.docx` notes into a structured consulting/private equity work brief.

## Features

- Input validation with clear errors
- Input support for `.txt` and `.docx` (Word)
- Modes: `internal`, `client`, `investment`
- Output sections in fixed order:
  - Situation
  - Key Findings
  - Risks
  - Open Questions
  - Next Steps
- Timestamped markdown output in `outputs/`
- Rule-based parsing with lightweight heuristics
- Auto-cleaning for transcript noise (timestamps, speaker labels, meeting metadata)
- Concise synthesis with section limits and a dedicated `Key Takeaways (KTAs)` section
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
briefsmith-agent meeting_transcript.docx --mode client
briefsmith-agent .\data\deal_notes.txt --mode investment
briefsmith-agent client_call.txt --mode client --output-dir outputs
```

## Test

```powershell
pytest -q
```
