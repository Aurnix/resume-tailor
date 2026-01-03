# CLAUDE.md

This file provides context for AI assistants working on this codebase.

## Project Overview

Resume Tailor is an AI-powered resume optimization tool that analyzes job descriptions and tailors resumes for maximum ATS compatibility. It uses the Anthropic Claude API for intelligent parsing, matching, and rewriting.

## Architecture

```
resume-tailor/
├── main.py                 # CLI entry point - orchestrates the pipeline
├── config.py               # Configuration dataclass (API keys, thresholds, weights)
├── core/                   # Core processing modules
│   ├── __init__.py         # Data models (dataclasses for parsed entities)
│   ├── jd_parser.py        # Job description extraction via Claude
│   ├── resume_analyzer.py  # Master resume parsing
│   ├── matcher.py          # Experience-to-requirements matching
│   ├── rewriter.py         # AI-powered bullet point optimization
│   └── scorer.py           # Fit scoring and gap analysis
├── output/
│   ├── docx_generator.js   # Word document creation (Node.js/docx library)
│   └── report_generator.py # Match report generation (Markdown/JSON)
└── utils/
    ├── web_fetcher.py      # URL content extraction for job postings
    └── text_utils.py       # Text processing helpers (slugify, etc.)
```

## Tech Stack

- **Python 3.10+**: Main language
- **Node.js**: Used only for docx generation (`output/docx_generator.js`)
- **Anthropic Claude API**: Powers all AI features (parsing, matching, rewriting)
- **Key Python deps**: `anthropic`, `requests`, `beautifulsoup4`, `pydantic`
- **Key Node deps**: `docx` (for Word document generation)

## Running the Project

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run with URL
python main.py -r resume.md -j "https://jobs.example.com/posting"

# Run with local file
python main.py -r resume.md -j job_description.txt

# Dry run (analysis only)
python main.py -r resume.md -j jd.txt --dry-run
```

## Key Data Flow

1. **Input**: Master resume (Markdown) + Job description (URL or text)
2. **JD Parsing** (`jd_parser.py`): Extracts skills, requirements, keywords via Claude
3. **Resume Analysis** (`resume_analyzer.py`): Parses resume into structured roles/bullets
4. **Matching** (`matcher.py`): Maps each bullet to JD requirements, scores relevance
5. **Scoring** (`scorer.py`): Calculates overall fit, identifies gaps
6. **Rewriting** (`rewriter.py`): Optimizes bullets with keyword injection
7. **Output**: ATS-friendly .docx + analysis report

## Configuration (`config.py`)

Key settings to know:
- `MODEL`: Default is `claude-sonnet-4-20250514` for most operations
- `MODEL_COMPLEX`: Uses `claude-opus-4-20250514` for complex analysis
- `MAX_BULLETS_PER_ROLE`: 6 (limits bullets shown per job)
- `MIN_MATCH_SCORE_TO_INCLUDE`: 0.25 (threshold for including bullets)
- `WEIGHT_*`: Scoring weights for required skills, experience match, etc.

## Code Patterns

- **Data models**: Defined as dataclasses in `core/__init__.py`
- **Claude prompts**: Embedded in each module (e.g., `JD_EXTRACTION_PROMPT` in `jd_parser.py`)
- **JSON extraction**: Claude returns JSON; modules use regex to extract from potential markdown wrapping
- **Error handling**: Raises `ValueError` for parse failures; CLI exits with status codes

## Common Development Tasks

### Adding a new skill category
Edit the `Skill` dataclass in `core/__init__.py` and update `jd_parser.py` prompt.

### Modifying scoring weights
Edit `Config` dataclass in `config.py` - weights are `WEIGHT_REQUIRED_SKILLS`, `WEIGHT_PREFERRED_SKILLS`, etc.

### Changing output format
- Markdown reports: `output/report_generator.py`
- Word documents: `output/docx_generator.js`

### Adjusting Claude prompts
Each core module has its prompt as a module-level constant (e.g., `JD_EXTRACTION_PROMPT`, `MATCHING_PROMPT`).

## Testing

No test suite currently exists. To test manually:
```bash
python main.py -r examples/master_resume.md -j examples/sample_jd.txt --dry-run
```

## Notes

- The docx generation shells out to Node.js (`subprocess.run(["node", "output/docx_generator.js"])`)
- Resume input must be Markdown format
- Output files are saved to `./output/generated/` by default
- Web fetching includes a custom User-Agent to avoid blocks
