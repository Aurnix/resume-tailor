# Resume Tailor

**"I built this because applying to 200 jobs by hand is stupid."**

An AI-powered resume optimization tool that analyzes job descriptions and tailors your resume for maximum ATS compatibility and relevance.

## What It Does

1. **Parses job descriptions** - Extracts requirements, keywords, skills, and signals
2. **Matches your experience** - Maps your background to what they're asking for
3. **Rewrites strategically** - Reorders bullets, adjusts emphasis, injects keywords naturally
4. **Scores your fit** - Honest gap analysis and match percentage
5. **Exports ATS-friendly .docx** - Clean, parseable format

## Quick Start

### Web Interface (Recommended)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/resume-tailor.git
cd resume-tailor

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Start the backend (Terminal 1)
python api.py

# Start the frontend (Terminal 2)
cd frontend && npm run dev
```

Then open **http://localhost:5173** in your browser.

### CLI Usage

```bash
# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Run it
python main.py --resume your_master_resume.md --job "https://example.com/job-posting"
# OR
python main.py --resume your_master_resume.md --job job_description.txt
```

## Project Structure

```
resume-tailor/
├── main.py                 # CLI entry point
├── api.py                  # FastAPI backend for web interface
├── config.py               # Configuration and API settings
├── requirements.txt        # Python dependencies
├── package.json            # Node dependencies (for docx generation)
│
├── frontend/               # React web interface
│   ├── src/
│   │   ├── App.tsx         # Main application component
│   │   ├── api.ts          # API client functions
│   │   ├── types.ts        # TypeScript type definitions
│   │   ├── components/
│   │   │   ├── TailorForm.tsx      # Resume/job input form
│   │   │   ├── ProcessingView.tsx  # Progress display
│   │   │   └── ResultsView.tsx     # Results and download
│   │   └── hooks/
│   │       └── useTailoring.ts     # Tailoring state management
│   ├── package.json        # Frontend dependencies
│   └── vite.config.ts      # Vite configuration
│
├── core/
│   ├── __init__.py         # Data models (ParsedResume, ParsedJD, etc.)
│   ├── jd_parser.py        # Job description extraction
│   ├── resume_analyzer.py  # Master resume parsing
│   ├── matcher.py          # Experience-to-requirements matching
│   ├── rewriter.py         # AI-powered bullet rewriting
│   └── scorer.py           # Fit scoring and gap analysis
│
├── output/
│   ├── docx_generator.js   # Word document creation
│   └── report_generator.py # Match report generation
│
├── utils/
│   ├── web_fetcher.py      # URL content extraction
│   └── text_utils.py       # Text processing helpers
│
└── examples/
    └── sample_jd.txt       # Example job description
```

## How It Works

### 1. Job Description Analysis
```
Input: URL or raw text
   ↓
Extract: Required skills, preferred skills, responsibilities, 
         seniority signals, company context, red flags
   ↓
Output: Structured JD object with weighted requirements
```

### 2. Resume Matching
```
Input: Master resume + Parsed JD
   ↓
Process: Map each JD requirement to relevant experience
         Identify keyword gaps
         Score relevance of each bullet
   ↓
Output: Ranked experience items with match scores
```

### 3. Strategic Rewriting
```
Input: Matched experience + Target keywords
   ↓
Process: Reorder bullets (most relevant first)
         Inject missing keywords naturally
         Adjust quantified achievements for relevance
         Trim or expand based on fit
   ↓
Output: Tailored resume content
```

### 4. Document Generation
```
Input: Tailored content
   ↓
Process: Apply ATS-friendly formatting
         Generate clean .docx
         Create match report
   ↓
Output: resume_[company]_[date].docx + analysis.md
```

## Configuration

Edit `config.py` to customize:

```python
# API Settings
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-sonnet-4-20250514"  # or claude-opus-4-20250514 for complex JDs

# Output Settings
OUTPUT_DIR = "./output"
INCLUDE_MATCH_REPORT = True
INCLUDE_TALKING_POINTS = True

# Resume Settings
MAX_BULLETS_PER_ROLE = 6
MIN_MATCH_SCORE_TO_INCLUDE = 0.3
```

## Usage Examples

### Basic Usage
```bash
# From URL
python main.py -r master_resume.md -j "https://jobs.lever.co/company/position"

# From file
python main.py -r master_resume.md -j job_description.txt

# With company context
python main.py -r master_resume.md -j jd.txt --company "Acme Corp" --notes "referral from John"
```

### Output Options
```bash
# Just the resume
python main.py -r resume.md -j jd.txt --output resume_only

# Resume + full analysis
python main.py -r resume.md -j jd.txt --output full

# Dry run (see what would change without generating)
python main.py -r resume.md -j jd.txt --dry-run
```

## The Match Report

Each run generates a match report including:

- **Match Score**: Overall fit percentage
- **Keyword Coverage**: Which required terms you hit vs. miss
- **Gap Analysis**: What you're missing and how to address it
- **Talking Points**: Interview prep based on matched experience
- **Red Flags**: Potential concerns and how to preempt them

## Why This Exists

The job market is broken. ATS systems reject qualified candidates for missing keywords. Tailoring resumes by hand takes 30-60 minutes per application. At 200 applications, that's 100-200 hours of manual work.

This tool doesn't help you lie. It helps you present your real experience in the language each employer is looking for.

## Contributing

PRs welcome. Especially interested in:
- Additional ATS format testing
- Industry-specific keyword libraries
- Integration with job boards (LinkedIn, Indeed, etc.)

## License

MIT - Do whatever you want with it.

---

*Built out of frustration by someone who was tired of the job search grind.*
