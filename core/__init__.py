"""
Core module - Data models and types for Resume Tailor.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class SkillLevel(Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    NICE_TO_HAVE = "nice_to_have"


class SeniorityLevel(Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"


@dataclass
class Skill:
    """A skill extracted from JD or resume."""
    name: str
    level: SkillLevel = SkillLevel.PREFERRED
    category: str = "general"
    variations: List[str] = field(default_factory=list)
    
    def matches(self, other: str) -> bool:
        """Check if this skill matches a string (including variations)."""
        other_lower = other.lower()
        if self.name.lower() in other_lower or other_lower in self.name.lower():
            return True
        return any(v.lower() in other_lower or other_lower in v.lower() for v in self.variations)


@dataclass
class ParsedJobDescription:
    """Structured job description data."""
    title: str
    company: Optional[str]
    location: Optional[str]
    remote_status: Optional[str]  # remote, hybrid, onsite
    
    required_skills: List[Skill]
    preferred_skills: List[Skill]
    responsibilities: List[str]
    
    seniority: SeniorityLevel
    years_experience: Optional[int]
    education_required: Optional[str]
    
    salary_range: Optional[str]
    benefits_mentioned: List[str]
    
    # Extracted signals
    keywords: List[str]  # High-frequency terms
    action_verbs: List[str]  # Verbs they use (match these)
    red_flags: List[str]  # Concerning phrases
    culture_signals: List[str]  # What they value
    
    raw_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "remote_status": self.remote_status,
            "required_skills": [{"name": s.name, "category": s.category} for s in self.required_skills],
            "preferred_skills": [{"name": s.name, "category": s.category} for s in self.preferred_skills],
            "responsibilities": self.responsibilities,
            "seniority": self.seniority.value,
            "years_experience": self.years_experience,
            "keywords": self.keywords,
        }


@dataclass
class ContactInfo:
    """Resume contact information."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "website": self.website,
            "github": self.github,
        }


@dataclass
class Bullet:
    """A single resume bullet point."""
    text: str
    keywords: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)  # Quantified achievements
    action_verb: Optional[str] = None
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "keywords": self.keywords,
            "metrics": self.metrics,
        }


@dataclass
class Role:
    """A job role/position on resume."""
    title: str
    company: str
    start_date: str
    end_date: Optional[str]  # None = "Present"
    location: Optional[str]
    bullets: List[Bullet]
    summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "company": self.company,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "location": self.location,
            "bullets": [b.to_dict() for b in self.bullets],
            "summary": self.summary,
        }


@dataclass
class Education:
    """Education entry."""
    degree: str
    school: str
    graduation_date: Optional[str]
    gpa: Optional[str] = None
    honors: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "school": self.school,
            "graduation_date": self.graduation_date,
            "gpa": self.gpa,
            "honors": self.honors,
        }


@dataclass
class ParsedResume:
    """Structured resume data."""
    contact: ContactInfo
    summary: Optional[str]
    roles: List[Role]
    education: List[Education]
    skills: List[str]
    certifications: List[str]
    projects: List[Dict[str, Any]]
    
    raw_text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact": self.contact.to_dict(),
            "summary": self.summary,
            "roles": [r.to_dict() for r in self.roles],
            "education": [e.to_dict() for e in self.education],
            "skills": self.skills,
            "certifications": self.certifications,
            "projects": self.projects,
        }


@dataclass
class BulletMatch:
    """A match between a resume bullet and JD requirement."""
    original_bullet: str
    matched_requirements: List[str]
    matched_keywords: List[str]
    score: float  # 0.0 to 1.0
    role_title: str
    role_company: str
    suggested_rewrite: Optional[str] = None


@dataclass
class MatchResult:
    """Overall matching results."""
    bullet_matches: List[BulletMatch]
    skill_coverage: Dict[str, bool]  # skill -> matched?
    missing_keywords: List[str]
    keyword_suggestions: Dict[str, str]  # missing -> suggested insertion point
    overall_keyword_match: float


@dataclass
class FitAnalysis:
    """Complete fit analysis."""
    overall_score: float  # 0.0 to 1.0
    keywords_matched: int
    keywords_total: int
    
    score_breakdown: Dict[str, float]  # category -> score
    
    gaps: List[str]  # What's missing
    strengths: List[str]  # Strong matches
    talking_points: List[str]  # Interview prep
    red_flags: List[str]  # Concerns to address
    
    seniority_fit: str  # "underqualified", "match", "overqualified"
    salary_assessment: Optional[str]


@dataclass
class TailoredContent:
    """The final tailored resume content."""
    summary: str
    roles: List[Role]
    skills_section: List[str]  # Reordered/filtered skills
    
    # Metadata
    keywords_added: List[str]
    bullets_rewritten: int
    bullets_reordered: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "roles": [r.to_dict() for r in self.roles],
            "skills_section": self.skills_section,
            "keywords_added": self.keywords_added,
            "bullets_rewritten": self.bullets_rewritten,
            "bullets_reordered": self.bullets_reordered,
        }
