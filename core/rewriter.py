"""
Bullet Rewriter - Tailors resume content for specific jobs.
"""

import json
import re
from typing import List
import anthropic

from config import Config
from core import (
    ParsedResume,
    ParsedJobDescription,
    MatchResult,
    TailoredContent,
    Role,
    Bullet
)


REWRITE_PROMPT = """Tailor this resume content for the target job.

<target_job>
Title: {job_title}
Company: {company}

Required Skills: {required_skills}
Key Responsibilities: {responsibilities}
Keywords to include: {keywords}
Their action verbs: {action_verbs}
</target_job>

<current_resume>
Summary: {current_summary}

Experience:
{experience_json}

Skills: {skills}
</current_resume>

<match_analysis>
Top matched bullets (highest relevance): {top_matches}
Missing keywords to inject: {missing_keywords}
</match_analysis>

Create tailored content:

1. SUMMARY: Rewrite to directly address this role (max {max_summary_words} words)
   - Lead with most relevant experience
   - Include 2-3 of their keywords naturally
   - Match their seniority language

2. BULLETS: For each role, select and optimize bullets
   - Keep top {max_bullets} most relevant bullets per role
   - Reorder: most relevant first
   - Inject missing keywords naturally (don't force them)
   - Preserve all metrics and quantified achievements
   - Use their action verbs where appropriate
   - DON'T fabricate experience - only rephrase what exists

3. SKILLS: Reorder skills list
   - Required skills first
   - Preferred skills second
   - Other relevant skills third

Return JSON:
{{
    "summary": "Tailored summary text",
    "roles": [
        {{
            "title": "Job title",
            "company": "Company",
            "start_date": "Start",
            "end_date": "End or null",
            "bullets": [
                {{"text": "Tailored bullet 1", "was_rewritten": true}},
                {{"text": "Original bullet kept as-is", "was_rewritten": false}}
            ]
        }}
    ],
    "skills_section": ["Skill 1", "Skill 2", "Skill 3"],
    "keywords_added": ["keyword1", "keyword2"],
    "changes_made": ["Summary rewritten", "Bullet 3 in Role 1 updated to include 'data analysis'"]
}}

CRITICAL: 
- Never invent experience or metrics
- Only rephrase and reorganize existing content
- Inject keywords only where they fit naturally

Return ONLY valid JSON."""


class BulletRewriter:
    """Rewrites and optimizes resume content for specific jobs."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def rewrite(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        matches: MatchResult
    ) -> TailoredContent:
        """Rewrite resume content tailored to job description."""
        
        # Prepare experience data
        experience_data = []
        for role in resume.roles:
            experience_data.append({
                "title": role.title,
                "company": role.company,
                "start_date": role.start_date,
                "end_date": role.end_date,
                "bullets": [b.text for b in role.bullets]
            })
        
        # Get top matches for reference
        top_matches = sorted(
            matches.bullet_matches, 
            key=lambda m: m.score, 
            reverse=True
        )[:10]
        top_match_texts = [f"[{m.score:.0%}] {m.original_bullet[:100]}" for m in top_matches]
        
        # Call Claude
        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=self.config.MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": REWRITE_PROMPT.format(
                    job_title=jd.title,
                    company=jd.company or "the company",
                    required_skills=", ".join(s.name for s in jd.required_skills),
                    responsibilities="; ".join(jd.responsibilities[:5]),
                    keywords=", ".join(jd.keywords[:15]),
                    action_verbs=", ".join(jd.action_verbs[:10]),
                    current_summary=resume.summary or "No summary provided",
                    experience_json=json.dumps(experience_data, indent=2),
                    skills=", ".join(resume.skills[:20]),
                    top_matches="\n".join(top_match_texts),
                    missing_keywords=", ".join(matches.missing_keywords[:10]),
                    max_summary_words=self.config.MAX_SUMMARY_WORDS,
                    max_bullets=self.config.MAX_BULLETS_PER_ROLE
                )
            }]
        )
        
        response_text = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if not json_match:
            raise ValueError("Could not extract JSON from rewrite response")
        
        data = json.loads(json_match.group())
        
        return self._to_tailored_content(data, resume)
    
    def _to_tailored_content(
        self, 
        data: dict, 
        original_resume: ParsedResume
    ) -> TailoredContent:
        """Convert JSON response to TailoredContent."""
        
        # Build roles with bullets
        roles = []
        bullets_rewritten = 0
        bullets_reordered = 0
        
        for role_data in data.get("roles", []):
            bullets = []
            for b in role_data.get("bullets", []):
                if isinstance(b, dict):
                    bullets.append(Bullet(text=b.get("text", "")))
                    if b.get("was_rewritten"):
                        bullets_rewritten += 1
                else:
                    bullets.append(Bullet(text=str(b)))
            
            role = Role(
                title=role_data.get("title", ""),
                company=role_data.get("company", ""),
                start_date=role_data.get("start_date", ""),
                end_date=role_data.get("end_date"),
                location=None,
                bullets=bullets
            )
            roles.append(role)
            
            # Rough estimate of reordering
            if len(bullets) > 1:
                bullets_reordered += 1
        
        return TailoredContent(
            summary=data.get("summary", ""),
            roles=roles,
            skills_section=data.get("skills_section", []),
            keywords_added=data.get("keywords_added", []),
            bullets_rewritten=bullets_rewritten,
            bullets_reordered=bullets_reordered
        )
    
    def rewrite_single_bullet(
        self,
        bullet: str,
        target_keywords: List[str],
        action_verbs: List[str]
    ) -> str:
        """Rewrite a single bullet to better match job requirements."""
        
        prompt = f"""Rewrite this resume bullet to better match the target job.

Original bullet: {bullet}

Target keywords to include (if natural): {', '.join(target_keywords)}
Preferred action verbs: {', '.join(action_verbs)}

Rules:
- Keep all metrics and numbers exactly as stated
- Don't invent new achievements
- Only include keywords that fit naturally
- Keep similar length (within 20%)

Return ONLY the rewritten bullet text, nothing else."""

        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
