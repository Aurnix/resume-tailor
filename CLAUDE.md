# CLAUDE.md

## Project Overview

Resume Tailor is an AI-powered resume optimization tool that analyzes job descriptions and tailors resumes for maximum ATS compatibility. It uses the Anthropic API to parse JDs, match experience, rewrite bullets, and score fit.

## Tech Stack

- **Python 3.x**: Core application logic
- **Node.js**: DOCX file generation (uses `docx` npm package)
- **Anthropic API**: AI-powered text analysis and generation

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run the tool
python main.py -r resume.md -j "https://example.com/job-posting"
python main.py -r resume.md -j job_description.txt --company "Acme Corp"

# Dry run (analysis only, no file generation)
python main.py -r resume.md -j jd.txt --dry-run
```

## Project Structure

```
resume-tailor/
├── main.py                 # CLI entry point (argparse)
├── config.py               # Config dataclass with API/output settings
├── core/                   # Core processing modules
│   ├── jd_parser.py        # Job description extraction via Claude
│   ├── resume_analyzer.py  # Master resume parsing
│   ├── matcher.py          # Experience-to-requirements matching
│   ├── rewriter.py         # AI-powered bullet rewriting
│   └── scorer.py           # Fit scoring and gap analysis
├── output/
│   ├── docx_generator.js   # Node.js script for Word doc generation
│   └── report_generator.py # Match report generation (markdown/JSON)
├── utils/
│   ├── web_fetcher.py      # URL content extraction
│   └── text_utils.py       # Text processing helpers (slugify, etc.)
├── prompts/                # Prompt templates (*.txt files)
└── templates/              # Resume structure templates
```

## Key Patterns

### Configuration
Config is a dataclass in `config.py`. Access via `Config()` instance or `get_config()` singleton. Key settings:
- `ANTHROPIC_API_KEY`: From environment variable
- `MODEL`: Default model for API calls (`claude-sonnet-4-20250514`)
- `OUTPUT_DIR`: Where generated files go (`./output/generated`)

### Data Models
Located in `core/__init__.py`. Uses dataclasses/pydantic:
- `ParsedJobDescription`: Structured JD data
- `ParsedResume`: Structured resume data
- `Skill`, `SkillLevel`, `SeniorityLevel`: Enums and models

### API Calls
All Claude API calls use the `anthropic` Python SDK:
```python
client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
response = client.messages.create(
    model=self.config.MODEL,
    max_tokens=self.config.MAX_TOKENS,
    messages=[{"role": "user", "content": prompt}]
)
```

### Python/Node.js Interop
DOCX generation calls Node.js via subprocess with JSON on stdin:
```python
subprocess.run(
    ["node", "output/docx_generator.js"],
    input=json.dumps(data),
    capture_output=True,
    text=True
)
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |

## Development Notes

- Prompts are stored as `.txt` files in `prompts/` directory
- Output files are named `resume_[company-slug]_[date].docx`
- Match reports are generated as `*_analysis.md` or `*_analysis.json`
- Web fetching uses custom user agent to avoid blocking
