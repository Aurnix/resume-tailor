"""
Experience Matcher - Maps resume experience to job requirements.
"""

import json
import re
from typing import List, Dict
import anthropic

from config import Config
from core import (
    ParsedResume,
    ParsedJobDescription,
    BulletMatch,
    MatchResult,
    Skill
)


MATCHING_PROMPT = """You are matching resume experience to job requirements.

<job_requirements>
Title: {job_title}
Company: {company}

Required Skills:
{required_skills}

Preferred Skills:
{preferred_skills}

Key Responsibilities:
{responsibilities}

Important Keywords: {keywords}
</job_requirements>

<resume_bullets>
{bullets_json}
</resume_bullets>

For each resume bullet, analyze how well it matches the job requirements.

Return JSON:
{{
    "bullet_matches": [
        {{
            "bullet_index": 0,
            "score": 0.85,
            "matched_requirements": ["requirement 1", "requirement 2"],
            "matched_keywords": ["keyword1", "keyword2"],
            "suggested_rewrite": "Improved bullet text with better keyword integration, or null if good as-is"
        }}
    ],
    "skill_coverage": {{
        "skill_name": true,
        "another_skill": false
    }},
    "missing_keywords": ["keyword not found in resume"],
    "keyword_suggestions": {{
        "missing_keyword": "Suggested bullet index or section to add it"
    }}
}}

Scoring guidelines:
- 0.9-1.0: Direct match to primary responsibility, uses their keywords
- 0.7-0.89: Strong match to secondary responsibility or required skill
- 0.5-0.69: Moderate match, transferable experience
- 0.3-0.49: Weak match, tangentially related
- 0.0-0.29: No meaningful match

For suggested_rewrite:
- Only suggest if score < 0.8 AND rewrite would improve match
- Inject missing keywords naturally
- Keep metrics and achievements intact
- Match their action verb style

Return ONLY valid JSON."""


class ExperienceMatcher:
    """Matches resume bullets to job requirements."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def match(
        self, 
        resume: ParsedResume, 
        jd: ParsedJobDescription
    ) -> MatchResult:
        """Match resume experience to job requirements."""
        
        # Prepare bullets for matching
        bullets_data = []
        for role in resume.roles:
            for bullet in role.bullets:
                bullets_data.append({
                    "text": bullet.text,
                    "role_title": role.title,
                    "role_company": role.company,
                    "keywords": bullet.keywords,
                    "metrics": bullet.metrics
                })
        
        # Format skills for prompt
        required_skills = "\n".join(f"- {s.name}" for s in jd.required_skills)
        preferred_skills = "\n".join(f"- {s.name}" for s in jd.preferred_skills)
        responsibilities = "\n".join(f"- {r}" for r in jd.responsibilities)
        
        # Call Claude
        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=self.config.MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": MATCHING_PROMPT.format(
                    job_title=jd.title,
                    company=jd.company or "Unknown",
                    required_skills=required_skills or "Not specified",
                    preferred_skills=preferred_skills or "Not specified",
                    responsibilities=responsibilities or "Not specified",
                    keywords=", ".join(jd.keywords),
                    bullets_json=json.dumps(bullets_data, indent=2)
                )
            }]
        )
        
        response_text = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if not json_match:
            raise ValueError("Could not extract JSON from matching response")
        
        data = json.loads(json_match.group())
        
        return self._to_match_result(data, bullets_data, jd)
    
    def _to_match_result(
        self, 
        data: dict, 
        bullets_data: List[dict],
        jd: ParsedJobDescription
    ) -> MatchResult:
        """Convert JSON response to MatchResult."""
        
        bullet_matches = []
        for match in data.get("bullet_matches", []):
            idx = match.get("bullet_index", 0)
            if idx < len(bullets_data):
                bullet_info = bullets_data[idx]
                bullet_matches.append(BulletMatch(
                    original_bullet=bullet_info["text"],
                    matched_requirements=match.get("matched_requirements", []),
                    matched_keywords=match.get("matched_keywords", []),
                    score=match.get("score", 0.0),
                    role_title=bullet_info["role_title"],
                    role_company=bullet_info["role_company"],
                    suggested_rewrite=match.get("suggested_rewrite")
                ))
        
        # Calculate overall keyword match
        all_keywords = set(jd.keywords)
        all_keywords.update(s.name.lower() for s in jd.required_skills)
        all_keywords.update(s.name.lower() for s in jd.preferred_skills)
        
        matched_keywords = set()
        for bm in bullet_matches:
            matched_keywords.update(k.lower() for k in bm.matched_keywords)
        
        if all_keywords:
            overall_match = len(matched_keywords & all_keywords) / len(all_keywords)
        else:
            overall_match = 0.5
        
        return MatchResult(
            bullet_matches=bullet_matches,
            skill_coverage=data.get("skill_coverage", {}),
            missing_keywords=data.get("missing_keywords", []),
            keyword_suggestions=data.get("keyword_suggestions", {}),
            overall_keyword_match=overall_match
        )
    
    def get_top_matches(
        self, 
        match_result: MatchResult, 
        n: int = 10
    ) -> List[BulletMatch]:
        """Get the top N matching bullets."""
        sorted_matches = sorted(
            match_result.bullet_matches, 
            key=lambda m: m.score, 
            reverse=True
        )
        return sorted_matches[:n]
    
    def get_matches_by_role(
        self, 
        match_result: MatchResult
    ) -> Dict[str, List[BulletMatch]]:
        """Group matches by role for easier processing."""
        by_role = {}
        for match in match_result.bullet_matches:
            key = f"{match.role_company} - {match.role_title}"
            if key not in by_role:
                by_role[key] = []
            by_role[key].append(match)
        
        # Sort each role's bullets by score
        for key in by_role:
            by_role[key].sort(key=lambda m: m.score, reverse=True)
        
        return by_role
