"""
Resume Analyzer - Parses master resume into structured data.
"""

import json
import re
from typing import List, Dict, Any
import anthropic

from config import Config
from core import (
    ParsedResume,
    ContactInfo,
    Role,
    Bullet,
    Education
)


RESUME_EXTRACTION_PROMPT = """Parse this resume into structured JSON format.

<resume>
{resume_text}
</resume>

Extract and return as JSON:

{{
    "contact": {{
        "name": "Full name",
        "email": "email or null",
        "phone": "phone or null",
        "location": "location or null",
        "linkedin": "linkedin url or null",
        "website": "website or null",
        "github": "github or null"
    }},
    
    "summary": "Professional summary paragraph or null",
    
    "roles": [
        {{
            "title": "Job title",
            "company": "Company name",
            "start_date": "Start date",
            "end_date": "End date or null if current",
            "location": "Location or null",
            "summary": "Role summary if present, else null",
            "bullets": [
                {{
                    "text": "Full bullet text",
                    "keywords": ["extracted", "keywords", "skills"],
                    "metrics": ["$2.5M", "40%", "122 accounts"],
                    "action_verb": "Led"
                }}
            ]
        }}
    ],
    
    "education": [
        {{
            "degree": "Degree name",
            "school": "School name",
            "graduation_date": "Date or null",
            "gpa": "GPA or null",
            "honors": "Honors or null"
        }}
    ],
    
    "skills": ["skill1", "skill2", "skill3"],
    
    "certifications": ["cert1", "cert2"],
    
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"],
            "url": "url or null"
        }}
    ]
}}

Guidelines:
- Extract ALL bullet points, preserving original text exactly
- For each bullet, identify: keywords (skills/tools), metrics (numbers/percentages/$), action verb
- Preserve date formats as written
- If something is unclear or missing, use null
- Skills section should be a flat list of all skills mentioned

Return ONLY valid JSON."""


class ResumeAnalyzer:
    """Parses resumes into structured data using Claude."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def parse(self, resume_text: str) -> ParsedResume:
        """Parse a resume into structured format."""
        
        # Call Claude for extraction
        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=self.config.MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text)
                }
            ]
        )
        
        response_text = response.content[0].text
        
        # Extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            raise ValueError("Could not extract JSON from Claude response")
        
        data = json.loads(json_match.group())
        
        return self._to_parsed_resume(data, resume_text)
    
    def _to_parsed_resume(self, data: dict, raw_text: str) -> ParsedResume:
        """Convert parsed JSON to ParsedResume dataclass."""
        
        # Parse contact
        contact_data = data.get("contact", {})
        contact = ContactInfo(
            name=contact_data.get("name", "Unknown"),
            email=contact_data.get("email"),
            phone=contact_data.get("phone"),
            location=contact_data.get("location"),
            linkedin=contact_data.get("linkedin"),
            website=contact_data.get("website"),
            github=contact_data.get("github")
        )
        
        # Parse roles
        roles = []
        for role_data in data.get("roles", []):
            bullets = [
                Bullet(
                    text=b.get("text", ""),
                    keywords=b.get("keywords", []),
                    metrics=b.get("metrics", []),
                    action_verb=b.get("action_verb")
                )
                for b in role_data.get("bullets", [])
            ]
            
            role = Role(
                title=role_data.get("title", "Unknown"),
                company=role_data.get("company", "Unknown"),
                start_date=role_data.get("start_date", ""),
                end_date=role_data.get("end_date"),
                location=role_data.get("location"),
                bullets=bullets,
                summary=role_data.get("summary")
            )
            roles.append(role)
        
        # Parse education
        education = [
            Education(
                degree=e.get("degree", ""),
                school=e.get("school", ""),
                graduation_date=e.get("graduation_date"),
                gpa=e.get("gpa"),
                honors=e.get("honors")
            )
            for e in data.get("education", [])
        ]
        
        return ParsedResume(
            contact=contact,
            summary=data.get("summary"),
            roles=roles,
            education=education,
            skills=data.get("skills", []),
            certifications=data.get("certifications", []),
            projects=data.get("projects", []),
            raw_text=raw_text
        )
    
    def extract_all_keywords(self, parsed_resume: ParsedResume) -> List[str]:
        """Extract all unique keywords from a parsed resume."""
        keywords = set()
        
        # From skills section
        keywords.update(parsed_resume.skills)
        
        # From bullets
        for role in parsed_resume.roles:
            for bullet in role.bullets:
                keywords.update(bullet.keywords)
        
        # From certifications
        keywords.update(parsed_resume.certifications)
        
        return sorted(list(keywords))
    
    def get_experience_years(self, parsed_resume: ParsedResume) -> int:
        """Estimate total years of experience from resume."""
        # This is a rough estimate - could be improved with date parsing
        if not parsed_resume.roles:
            return 0
        
        # Count roles and estimate
        # Most roles are 1-3 years, so use 2 as average
        return len(parsed_resume.roles) * 2
