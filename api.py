"""
FastAPI backend for Resume Tailor web interface.
"""

import uuid
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import Config
from core.jd_parser import JobDescriptionParser
from core.resume_analyzer import ResumeAnalyzer
from core.matcher import ExperienceMatcher
from core.rewriter import BulletRewriter
from core.scorer import FitScorer
from output.report_generator import ReportGenerator
from utils.web_fetcher import fetch_job_posting
from utils.text_utils import slugify

import subprocess
import json
import os


# In-memory job storage (for MVP - would use Redis/DB in production)
jobs: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure output directory exists
    Path("output/generated").mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Resume Tailor API",
    description="AI-powered resume optimization for job applications",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TailorRequest(BaseModel):
    resume_text: str
    job_description: str  # URL or raw text
    company_name: Optional[str] = None
    notes: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    current_step: int
    total_steps: int
    step_description: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def process_tailoring_job(job_id: str, resume_text: str, job_description: str,
                          company_name: Optional[str], notes: Optional[str]):
    """Process a resume tailoring job (runs in background)."""
    try:
        config = Config()

        # Validate API key
        if not config.ANTHROPIC_API_KEY:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "ANTHROPIC_API_KEY not configured on server"
            return

        # Load job description (from URL if needed)
        jobs[job_id]["current_step"] = 1
        jobs[job_id]["step_description"] = "Fetching job description..."

        if job_description.startswith(("http://", "https://")):
            try:
                jd_text = fetch_job_posting(job_description)
            except Exception as e:
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = f"Failed to fetch job posting: {str(e)}"
                return
        else:
            jd_text = job_description

        # Step 1: Parse job description
        jobs[job_id]["current_step"] = 1
        jobs[job_id]["step_description"] = "Analyzing job description..."
        jd_parser = JobDescriptionParser(config)
        parsed_jd = jd_parser.parse(jd_text)

        if company_name:
            parsed_jd.company = company_name

        # Step 2: Analyze resume
        jobs[job_id]["current_step"] = 2
        jobs[job_id]["step_description"] = "Parsing resume..."
        resume_analyzer = ResumeAnalyzer(config)
        parsed_resume = resume_analyzer.parse(resume_text)

        # Step 3: Match experience
        jobs[job_id]["current_step"] = 3
        jobs[job_id]["step_description"] = "Matching experience to requirements..."
        matcher = ExperienceMatcher(config)
        matches = matcher.match(parsed_resume, parsed_jd)

        # Step 4: Score fit
        jobs[job_id]["current_step"] = 4
        jobs[job_id]["step_description"] = "Calculating fit score..."
        scorer = FitScorer(config)
        fit_analysis = scorer.score(parsed_resume, parsed_jd, matches)

        # Step 5: Rewrite and generate
        jobs[job_id]["current_step"] = 5
        jobs[job_id]["step_description"] = "Tailoring resume content..."
        rewriter = BulletRewriter(config)
        tailored_content = rewriter.rewrite(parsed_resume, parsed_jd, matches)

        # Generate outputs
        output_dir = Path(config.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        company_slug = slugify(parsed_jd.company or "unknown")
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"resume_{company_slug}_{date_str}"

        # Generate .docx
        docx_path = output_dir / f"{base_filename}.docx"

        docx_data = {
            "content": tailored_content.to_dict(),
            "output_path": str(docx_path),
            "contact": parsed_resume.contact.to_dict()
        }

        result = subprocess.run(
            ["node", "output/docx_generator.js"],
            input=json.dumps(docx_data),
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        docx_generated = result.returncode == 0

        # Build result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["current_step"] = 5
        jobs[job_id]["step_description"] = "Complete!"
        jobs[job_id]["result"] = {
            "fit_score": fit_analysis.overall_score,
            "keywords_matched": fit_analysis.keywords_matched,
            "keywords_total": fit_analysis.keywords_total,
            "gaps": fit_analysis.gaps,
            "strengths": fit_analysis.strengths,
            "talking_points": fit_analysis.talking_points,
            "seniority_fit": fit_analysis.seniority_fit,
            "job_title": parsed_jd.title,
            "company": parsed_jd.company,
            "docx_filename": f"{base_filename}.docx" if docx_generated else None,
            "tailored_summary": tailored_content.summary,
            "bullets_rewritten": tailored_content.bullets_rewritten,
            "keywords_added": tailored_content.keywords_added,
        }

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/api/tailor", response_model=JobStatus)
async def start_tailoring(request: TailorRequest, background_tasks: BackgroundTasks):
    """Start a new resume tailoring job."""
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "current_step": 0,
        "total_steps": 5,
        "step_description": "Starting...",
        "result": None,
        "error": None,
    }

    # Run processing in background
    background_tasks.add_task(
        process_tailoring_job,
        job_id,
        request.resume_text,
        request.job_description,
        request.company_name,
        request.notes
    )

    return JobStatus(**jobs[job_id])


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a tailoring job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(**jobs[job_id])


@app.get("/api/download/{filename}")
async def download_resume(filename: str):
    """Download a generated resume file."""
    file_path = Path("output/generated") / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    config = Config()
    return {
        "status": "healthy",
        "api_key_configured": bool(config.ANTHROPIC_API_KEY),
    }


# Serve frontend static files in production
frontend_path = Path(__file__).parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
