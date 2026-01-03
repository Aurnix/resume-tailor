"""
Configuration settings for Resume Tailor.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Application configuration."""
    
    # API Settings
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    MODEL: str = "claude-sonnet-4-20250514"  # Fast and capable
    MODEL_COMPLEX: str = "claude-opus-4-20250514"  # For complex analysis
    MAX_TOKENS: int = 4096
    
    # Output Settings
    OUTPUT_DIR: str = "./output/generated"
    INCLUDE_MATCH_REPORT: bool = True
    INCLUDE_TALKING_POINTS: bool = True
    INCLUDE_COVER_LETTER_DRAFT: bool = False
    
    # Resume Tailoring Settings
    MAX_BULLETS_PER_ROLE: int = 6
    MIN_BULLETS_PER_ROLE: int = 3
    MIN_MATCH_SCORE_TO_INCLUDE: float = 0.25
    KEYWORD_INJECTION_THRESHOLD: float = 0.5
    
    # Scoring Weights
    WEIGHT_REQUIRED_SKILLS: float = 0.4
    WEIGHT_PREFERRED_SKILLS: float = 0.2
    WEIGHT_EXPERIENCE_MATCH: float = 0.25
    WEIGHT_SENIORITY_FIT: float = 0.15
    
    # Content Limits
    MAX_SUMMARY_WORDS: int = 50
    MAX_BULLET_WORDS: int = 30
    MIN_BULLET_WORDS: int = 10
    
    # Web Fetching
    REQUEST_TIMEOUT: int = 30
    USER_AGENT: str = "Mozilla/5.0 (compatible; ResumeTailor/1.0)"
    
    # Prompts Directory
    PROMPTS_DIR: str = "./prompts"
    
    def get_prompt(self, prompt_name: str) -> str:
        """Load a prompt template from file."""
        prompt_path = os.path.join(self.PROMPTS_DIR, f"{prompt_name}.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")


# Singleton instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get or create config singleton."""
    global _config
    if _config is None:
        _config = Config()
    return _config
