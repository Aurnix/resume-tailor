# CLAUDE.md

This file provides context to Claude Code about this project.

## Project Overview

Resume Tailor is an AI-powered resume optimization tool that tailors resumes to specific job descriptions. It uses Claude AI to analyze job postings, match experience, and rewrite resume content for maximum relevance and ATS compatibility.

## Architecture

### Backend
- **CLI**: `main.py` - Command-line interface for direct usage
- **API**: `api.py` - FastAPI server for web interface
- **Core processing pipeline** (5 steps):
  1. `core/jd_parser.py` - Parse job description → extract skills, requirements, keywords
  2. `core/resume_analyzer.py` - Parse master resume → extract roles, bullets, skills
  3. `core/matcher.py` - Match resume bullets to job requirements (0.0-1.0 scores)
  4. `core/scorer.py` - Calculate overall fit score and gap analysis
  5. `core/rewriter.py` - Rewrite and reorder bullets, inject keywords

### Frontend
- **React + Vite + TypeScript** in `frontend/`
- **Tailwind CSS** for styling
- Components:
  - `TailorForm` - Input form for resume and job description
  - `ProcessingView` - Shows progress through 5-step pipeline
  - `ResultsView` - Displays results with download button

### Output Generation
- `output/docx_generator.js` - Node.js script for ATS-friendly .docx creation
- `output/report_generator.py` - Markdown/JSON analysis reports

## Key Data Models (in `core/__init__.py`)

- `ParsedJobDescription` - Structured JD with skills, responsibilities, seniority
- `ParsedResume` - Structured resume with contact, roles, bullets, skills
- `BulletMatch` - Match between resume bullet and JD requirement (with score)
- `FitAnalysis` - Overall fit score, gaps, strengths, talking points
- `TailoredContent` - Final rewritten resume content

## Running the Application

### Web Interface
```bash
# Terminal 1: Backend
python api.py

# Terminal 2: Frontend
cd frontend && npm run dev
```
Open http://localhost:5173

### CLI
```bash
python main.py --resume resume.md --job "https://example.com/job" --verbose
```

## Environment Variables

- `ANTHROPIC_API_KEY` (required) - Claude API key

## API Endpoints

- `POST /api/tailor` - Start tailoring job (returns job_id)
- `GET /api/jobs/{job_id}` - Poll job status and results
- `GET /api/download/{filename}` - Download generated .docx
- `GET /api/health` - Health check

## Development Notes

- Resume input must be in Markdown format
- Job descriptions can be URLs (auto-fetched) or raw text
- The tool rewrites but never fabricates experience
- All Claude API calls use structured JSON output
- Frontend proxies `/api` to backend via Vite config
