"""
Job Description Parser - Extracts structured data from job postings.
"""

import json
import re
from typing import Optional
import anthropic

from config import Config
from core import (
    ParsedJobDescription, 
    Skill, 
    SkillLevel, 
    SeniorityLevel
)


JD_EXTRACTION_PROMPT = """Analyze this job description and extract structured information.

<job_description>
{jd_text}
</job_description>

Extract the following and return as JSON:

{{
    "title": "Job title",
    "company": "Company name or null",
    "location": "Location or null",
    "remote_status": "remote" | "hybrid" | "onsite" | null,
    
    "required_skills": [
        {{"name": "skill name", "category": "technical|soft|domain|tool"}}
    ],
    "preferred_skills": [
        {{"name": "skill name", "category": "technical|soft|domain|tool"}}
    ],
    
    "responsibilities": ["key responsibility 1", "key responsibility 2"],
    
    "seniority": "entry" | "mid" | "senior" | "lead" | "manager" | "director" | "vp" | "c_level",
    "years_experience": number or null,
    "education_required": "degree requirement or null",
    
    "salary_range": "salary info or null",
    "benefits_mentioned": ["benefit 1", "benefit 2"],
    
    "keywords": ["high frequency important terms to include in resume"],
    "action_verbs": ["verbs they use like 'drive', 'lead', 'build'"],
    "red_flags": ["concerning phrases like 'wear many hats', 'fast-paced'"],
    "culture_signals": ["what they value: 'collaborative', 'data-driven'"]
}}

Guidelines:
- required_skills: Explicitly stated as required, must-have, or essential
- preferred_skills: Nice-to-have, bonus, or implied from responsibilities
- keywords: Terms that appear multiple times or are clearly important (these should go in the resume)
- action_verbs: The verbs they use to describe work - mirror these in resume bullets
- red_flags: "Startup mentality", "wear many hats", "unlimited PTO", "like a family"
- Infer seniority from title, years required, and scope of responsibilities

Return ONLY valid JSON, no other text."""


class JobDescriptionParser:
    """Parses job descriptions into structured data using Claude."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def parse(self, jd_text: str) -> ParsedJobDescription:
        """Parse a job description into structured format."""
        
        # Clean input
        jd_text = self._clean_text(jd_text)
        
        # Call Claude for extraction
        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=self.config.MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": JD_EXTRACTION_PROMPT.format(jd_text=jd_text)
                }
            ]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Extract JSON from response (handle potential markdown wrapping)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError("Could not extract JSON from Claude response")
        
        data = json.loads(json_match.group())
        
        # Convert to dataclass
        return self._to_parsed_jd(data, jd_text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize job description text."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove common cruft
        text = re.sub(r'Apply Now.*$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'Share this job.*$', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        return text.strip()
    
    def _to_parsed_jd(self, data: dict, raw_text: str) -> ParsedJobDescription:
        """Convert parsed JSON to ParsedJobDescription dataclass."""
        
        # Parse skills
        required_skills = [
            Skill(
                name=s["name"],
                level=SkillLevel.REQUIRED,
                category=s.get("category", "general")
            )
            for s in data.get("required_skills", [])
        ]
        
        preferred_skills = [
            Skill(
                name=s["name"],
                level=SkillLevel.PREFERRED,
                category=s.get("category", "general")
            )
            for s in data.get("preferred_skills", [])
        ]
        
        # Parse seniority
        seniority_map = {
            "entry": SeniorityLevel.ENTRY,
            "mid": SeniorityLevel.MID,
            "senior": SeniorityLevel.SENIOR,
            "lead": SeniorityLevel.LEAD,
            "manager": SeniorityLevel.MANAGER,
            "director": SeniorityLevel.DIRECTOR,
            "vp": SeniorityLevel.VP,
            "c_level": SeniorityLevel.C_LEVEL,
        }
        seniority = seniority_map.get(data.get("seniority", "mid"), SeniorityLevel.MID)
        
        return ParsedJobDescription(
            title=data.get("title", "Unknown Position"),
            company=data.get("company"),
            location=data.get("location"),
            remote_status=data.get("remote_status"),
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=data.get("responsibilities", []),
            seniority=seniority,
            years_experience=data.get("years_experience"),
            education_required=data.get("education_required"),
            salary_range=data.get("salary_range"),
            benefits_mentioned=data.get("benefits_mentioned", []),
            keywords=data.get("keywords", []),
            action_verbs=data.get("action_verbs", []),
            red_flags=data.get("red_flags", []),
            culture_signals=data.get("culture_signals", []),
            raw_text=raw_text
        )
    
    def extract_keywords_only(self, jd_text: str) -> list[str]:
        """Quick extraction of just keywords (for simple use cases)."""
        
        prompt = f"""Extract the most important keywords from this job description that should appear in a tailored resume.

<job_description>
{jd_text}
</job_description>

Return ONLY a JSON array of strings, like: ["keyword1", "keyword2", "keyword3"]
Focus on: technical skills, tools, methodologies, and key responsibilities.
Limit to 20 most important terms."""

        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        
        if json_match:
            return json.loads(json_match.group())
        return []
