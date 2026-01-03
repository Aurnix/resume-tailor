#!/usr/bin/env python3
"""
Resume Tailor - AI-powered resume optimization for job applications.

Usage:
    python main.py --resume master_resume.md --job "https://example.com/job"
    python main.py -r resume.md -j job_description.txt --company "Acme Corp"
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from config import Config
from core.jd_parser import JobDescriptionParser
from core.resume_analyzer import ResumeAnalyzer
from core.matcher import ExperienceMatcher
from core.rewriter import BulletRewriter
from core.scorer import FitScorer
from output.report_generator import ReportGenerator
from utils.web_fetcher import fetch_job_posting
from utils.text_utils import slugify


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tailor your resume to job descriptions using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -r resume.md -j "https://jobs.lever.co/company/role"
  python main.py -r resume.md -j jd.txt --company "Acme Corp"
  python main.py -r resume.md -j jd.txt --dry-run
        """
    )
    
    parser.add_argument(
        "-r", "--resume",
        required=True,
        help="Path to your master resume (Markdown format)"
    )
    
    parser.add_argument(
        "-j", "--job",
        required=True,
        help="Job description: URL or path to text file"
    )
    
    parser.add_argument(
        "--company",
        default=None,
        help="Company name (auto-extracted if not provided)"
    )
    
    parser.add_argument(
        "--notes",
        default=None,
        help="Additional context (e.g., 'referral from John', 'dream job')"
    )
    
    parser.add_argument(
        "--output",
        choices=["resume_only", "full", "json"],
        default="full",
        help="Output format (default: full)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show analysis without generating files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed processing output"
    )
    
    return parser.parse_args()


def load_job_description(job_input: str) -> str:
    """Load JD from URL or file path."""
    if job_input.startswith(("http://", "https://")):
        print(f"📡 Fetching job posting from URL...")
        return fetch_job_posting(job_input)
    elif os.path.exists(job_input):
        print(f"📄 Loading job description from file...")
        with open(job_input, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Assume it's raw text
        return job_input


def load_master_resume(resume_path: str) -> str:
    """Load master resume from file."""
    if not os.path.exists(resume_path):
        print(f"❌ Error: Resume file not found: {resume_path}")
        sys.exit(1)
    
    with open(resume_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    args = parse_args()
    config = Config()
    
    print("\n" + "="*60)
    print("🎯 RESUME TAILOR")
    print("="*60 + "\n")
    
    # Validate API key
    if not config.ANTHROPIC_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Run: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)
    
    # Load inputs
    print("📥 Loading inputs...")
    master_resume = load_master_resume(args.resume)
    job_description = load_job_description(args.job)
    
    if args.verbose:
        print(f"   Resume: {len(master_resume):,} characters")
        print(f"   JD: {len(job_description):,} characters")
    
    # Step 1: Parse job description
    print("\n🔍 Step 1/5: Analyzing job description...")
    jd_parser = JobDescriptionParser(config)
    parsed_jd = jd_parser.parse(job_description)
    
    if args.verbose:
        print(f"   Company: {parsed_jd.company}")
        print(f"   Role: {parsed_jd.title}")
        print(f"   Required skills: {len(parsed_jd.required_skills)}")
        print(f"   Preferred skills: {len(parsed_jd.preferred_skills)}")
    
    # Override company if provided
    if args.company:
        parsed_jd.company = args.company
    
    # Step 2: Analyze master resume
    print("📋 Step 2/5: Parsing master resume...")
    resume_analyzer = ResumeAnalyzer(config)
    parsed_resume = resume_analyzer.parse(master_resume)
    
    if args.verbose:
        print(f"   Roles found: {len(parsed_resume.roles)}")
        print(f"   Total bullets: {sum(len(r.bullets) for r in parsed_resume.roles)}")
        print(f"   Skills identified: {len(parsed_resume.skills)}")
    
    # Step 3: Match experience to requirements
    print("🔗 Step 3/5: Matching experience to requirements...")
    matcher = ExperienceMatcher(config)
    matches = matcher.match(parsed_resume, parsed_jd)
    
    if args.verbose:
        print(f"   Strong matches: {len([m for m in matches.bullet_matches if m.score > 0.7])}")
        print(f"   Moderate matches: {len([m for m in matches.bullet_matches if 0.4 < m.score <= 0.7])}")
        print(f"   Weak matches: {len([m for m in matches.bullet_matches if m.score <= 0.4])}")
    
    # Step 4: Score overall fit
    print("📊 Step 4/5: Calculating fit score...")
    scorer = FitScorer(config)
    fit_analysis = scorer.score(parsed_resume, parsed_jd, matches)
    
    print(f"\n   {'='*40}")
    print(f"   📈 MATCH SCORE: {fit_analysis.overall_score:.0%}")
    print(f"   {'='*40}")
    print(f"   ✅ Keywords matched: {fit_analysis.keywords_matched}/{fit_analysis.keywords_total}")
    print(f"   ⚠️  Gaps identified: {len(fit_analysis.gaps)}")
    
    if args.dry_run:
        print("\n🏃 Dry run - stopping before file generation")
        print("\n📋 Would rewrite these bullets:")
        for match in sorted(matches.bullet_matches, key=lambda m: m.score, reverse=True)[:5]:
            print(f"   [{match.score:.0%}] {match.original_bullet[:60]}...")
        
        if fit_analysis.gaps:
            print("\n⚠️  Gap analysis:")
            for gap in fit_analysis.gaps[:3]:
                print(f"   • {gap}")
        
        print("\n✅ Dry run complete. Remove --dry-run to generate files.")
        return
    
    # Step 5: Rewrite and generate
    print("✍️  Step 5/5: Tailoring resume...")
    rewriter = BulletRewriter(config)
    tailored_content = rewriter.rewrite(parsed_resume, parsed_jd, matches)
    
    # Generate outputs
    print("\n📄 Generating outputs...")
    
    # Create output directory
    output_dir = Path(config.OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    company_slug = slugify(parsed_jd.company or "unknown")
    date_str = datetime.now().strftime("%Y%m%d")
    base_filename = f"resume_{company_slug}_{date_str}"
    
    # Generate .docx
    docx_path = output_dir / f"{base_filename}.docx"
    print(f"   📝 Generating {docx_path}...")
    
    # Call Node.js script for docx generation
    import subprocess
    import json
    
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
    
    if result.returncode != 0:
        print(f"   ❌ Error generating docx: {result.stderr}")
    else:
        print(f"   ✅ Resume saved: {docx_path}")
    
    # Generate match report
    if args.output in ["full", "json"]:
        report_generator = ReportGenerator(config)
        
        if args.output == "full":
            report_path = output_dir / f"{base_filename}_analysis.md"
            report_generator.generate_markdown(
                fit_analysis, matches, tailored_content, report_path
            )
            print(f"   ✅ Analysis saved: {report_path}")
        else:
            json_path = output_dir / f"{base_filename}_analysis.json"
            report_generator.generate_json(
                fit_analysis, matches, tailored_content, json_path
            )
            print(f"   ✅ JSON saved: {json_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ COMPLETE!")
    print("="*60)
    print(f"\n📈 Match Score: {fit_analysis.overall_score:.0%}")
    print(f"📄 Resume: {docx_path}")
    
    if fit_analysis.talking_points:
        print("\n💬 Key Talking Points:")
        for point in fit_analysis.talking_points[:3]:
            print(f"   • {point}")
    
    if fit_analysis.gaps:
        print("\n⚠️  Address These Gaps:")
        for gap in fit_analysis.gaps[:3]:
            print(f"   • {gap}")
    
    print("\n🚀 Good luck with your application!\n")


if __name__ == "__main__":
    main()
