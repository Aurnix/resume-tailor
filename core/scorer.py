"""
Fit Scorer - Analyzes overall fit and generates recommendations.
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
    FitAnalysis
)


SCORING_PROMPT = """Analyze how well this candidate fits the job and provide actionable insights.

<job_requirements>
Title: {job_title}
Company: {company}
Seniority: {seniority}
Required Years: {years_required}

Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Responsibilities: {responsibilities}
</job_requirements>

<candidate_profile>
Current/Recent Title: {candidate_title}
Total Experience: ~{experience_years} years
Skills: {candidate_skills}

Experience Highlights:
{experience_highlights}
</candidate_profile>

<keyword_analysis>
Keywords matched: {keywords_matched}
Keywords missing: {keywords_missing}
Overall keyword coverage: {keyword_coverage}%
</keyword_analysis>

Provide a comprehensive fit analysis:

{{
    "overall_score": 0.75,
    
    "score_breakdown": {{
        "required_skills": 0.8,
        "preferred_skills": 0.6,
        "experience_relevance": 0.75,
        "seniority_fit": 0.9
    }},
    
    "seniority_fit": "match" | "underqualified" | "overqualified",
    
    "gaps": [
        "Missing direct experience with [specific tool/skill]",
        "No explicit [responsibility] experience shown"
    ],
    
    "strengths": [
        "Strong match on [key requirement]",
        "[Quantified achievement] directly relevant to [responsibility]"
    ],
    
    "talking_points": [
        "When asked about [gap], pivot to [related experience]",
        "Emphasize [achievement] as it directly addresses [requirement]"
    ],
    
    "red_flags": [
        "May be perceived as [concern] - address by [strategy]"
    ],
    
    "salary_assessment": "Based on role level and market, expect $X-Y range"
}}

Be honest but constructive. Focus on actionable insights.
Return ONLY valid JSON."""


class FitScorer:
    """Scores candidate fit and generates analysis."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def score(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        matches: MatchResult
    ) -> FitAnalysis:
        """Generate comprehensive fit analysis."""
        
        # Calculate keyword stats
        all_keywords = set(k.lower() for k in jd.keywords)
        all_keywords.update(s.name.lower() for s in jd.required_skills)
        all_keywords.update(s.name.lower() for s in jd.preferred_skills)
        
        resume_keywords = set(s.lower() for s in resume.skills)
        for role in resume.roles:
            for bullet in role.bullets:
                resume_keywords.update(k.lower() for k in bullet.keywords)
        
        matched = all_keywords & resume_keywords
        missing = all_keywords - resume_keywords
        
        keyword_coverage = (len(matched) / len(all_keywords) * 100) if all_keywords else 50
        
        # Get experience highlights (top bullets)
        top_bullets = sorted(
            matches.bullet_matches,
            key=lambda m: m.score,
            reverse=True
        )[:5]
        experience_highlights = "\n".join(
            f"- [{m.score:.0%}] {m.original_bullet}" for m in top_bullets
        )
        
        # Estimate experience years
        experience_years = len(resume.roles) * 2  # Rough estimate
        
        # Call Claude for analysis
        response = self.client.messages.create(
            model=self.config.MODEL,
            max_tokens=self.config.MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": SCORING_PROMPT.format(
                    job_title=jd.title,
                    company=jd.company or "Unknown",
                    seniority=jd.seniority.value,
                    years_required=jd.years_experience or "Not specified",
                    required_skills=", ".join(s.name for s in jd.required_skills),
                    preferred_skills=", ".join(s.name for s in jd.preferred_skills),
                    responsibilities="; ".join(jd.responsibilities[:5]),
                    candidate_title=resume.roles[0].title if resume.roles else "Unknown",
                    experience_years=experience_years,
                    candidate_skills=", ".join(resume.skills[:20]),
                    experience_highlights=experience_highlights,
                    keywords_matched=", ".join(list(matched)[:15]),
                    keywords_missing=", ".join(list(missing)[:10]),
                    keyword_coverage=f"{keyword_coverage:.0f}"
                )
            }]
        )
        
        response_text = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        
        if not json_match:
            # Return basic analysis if parsing fails
            return self._basic_analysis(matched, all_keywords, keyword_coverage)
        
        data = json.loads(json_match.group())
        
        return FitAnalysis(
            overall_score=data.get("overall_score", 0.5),
            keywords_matched=len(matched),
            keywords_total=len(all_keywords),
            score_breakdown=data.get("score_breakdown", {}),
            gaps=data.get("gaps", []),
            strengths=data.get("strengths", []),
            talking_points=data.get("talking_points", []),
            red_flags=data.get("red_flags", []),
            seniority_fit=data.get("seniority_fit", "match"),
            salary_assessment=data.get("salary_assessment")
        )
    
    def _basic_analysis(
        self, 
        matched: set, 
        all_keywords: set,
        keyword_coverage: float
    ) -> FitAnalysis:
        """Generate basic analysis without Claude (fallback)."""
        return FitAnalysis(
            overall_score=keyword_coverage / 100,
            keywords_matched=len(matched),
            keywords_total=len(all_keywords),
            score_breakdown={
                "keyword_coverage": keyword_coverage / 100
            },
            gaps=[f"Missing keyword: {k}" for k in (all_keywords - matched)][:5],
            strengths=[f"Has keyword: {k}" for k in list(matched)[:5]],
            talking_points=[],
            red_flags=[],
            seniority_fit="match",
            salary_assessment=None
        )
    
    def quick_score(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription
    ) -> float:
        """Quick keyword-based score without full analysis."""
        
        all_keywords = set(k.lower() for k in jd.keywords)
        all_keywords.update(s.name.lower() for s in jd.required_skills)
        
        resume_text = resume.raw_text.lower()
        
        matches = sum(1 for k in all_keywords if k in resume_text)
        
        if not all_keywords:
            return 0.5
        
        return matches / len(all_keywords)
