"""
Text Utilities - Helper functions for text processing.
"""

import re
import unicodedata
from typing import List, Optional


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Example: "Acme Corp." -> "acme-corp"
    """
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Trim hyphens
    return text.strip('-')


def extract_metrics(text: str) -> List[str]:
    """
    Extract quantified metrics from text.
    
    Examples:
        - "$2.5M" 
        - "40%"
        - "122 accounts"
        - "20-30% growth"
    """
    patterns = [
        r'\$[\d,]+(?:\.\d+)?[KMB]?',           # Money: $2.5M, $100K
        r'\d+(?:\.\d+)?%',                      # Percentages: 40%, 20.5%
        r'\d+-\d+%',                            # Percentage ranges: 20-30%
        r'\d+(?:,\d{3})*\+?\s*(?:accounts?|clients?|users?|customers?|employees?|people|sites?|pages?|campaigns?)',  # Counts with units
        r'\d+x',                                 # Multipliers: 3x, 10x
        r'\d+(?:\.\d+)?\s*(?:hours?|days?|weeks?|months?|years?)',  # Time periods
    ]
    
    metrics = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metrics.extend(matches)
    
    return list(set(metrics))


def extract_action_verb(text: str) -> Optional[str]:
    """Extract the leading action verb from a bullet point."""
    
    # Common resume action verbs
    action_verbs = {
        'led', 'managed', 'directed', 'coordinated', 'developed', 'created',
        'built', 'designed', 'implemented', 'executed', 'delivered', 'achieved',
        'increased', 'decreased', 'reduced', 'improved', 'optimized', 'enhanced',
        'launched', 'established', 'pioneered', 'transformed', 'modernized',
        'analyzed', 'evaluated', 'assessed', 'researched', 'investigated',
        'collaborated', 'partnered', 'supported', 'assisted', 'facilitated',
        'trained', 'mentored', 'coached', 'educated', 'presented',
        'negotiated', 'secured', 'acquired', 'generated', 'produced',
        'architected', 'engineered', 'programmed', 'automated', 'integrated',
        'streamlined', 'consolidated', 'reorganized', 'restructured',
        'drove', 'spearheaded', 'championed', 'advocated', 'promoted',
        'maintained', 'sustained', 'preserved', 'ensured', 'guaranteed',
        'served', 'provided', 'offered', 'supplied', 'furnished',
        'oversaw', 'supervised', 'administered', 'governed', 'controlled',
        'resolved', 'addressed', 'handled', 'tackled', 'overcome',
        'identified', 'discovered', 'uncovered', 'recognized', 'detected'
    }
    
    # Get first word
    words = text.strip().split()
    if not words:
        return None
    
    first_word = words[0].lower().rstrip('ed').rstrip('ing')
    
    # Check if it's an action verb (or close to one)
    for verb in action_verbs:
        if first_word.startswith(verb[:4]):  # Fuzzy match on first 4 chars
            return words[0]
    
    return words[0] if words[0][0].isupper() else None


def clean_bullet(text: str) -> str:
    """Clean a bullet point for consistent formatting."""
    
    # Remove leading bullets/dashes
    text = re.sub(r'^[\s\-•*]+', '', text)
    
    # Ensure first letter is capitalized
    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
    
    # Remove trailing period if present (style preference)
    # text = text.rstrip('.')
    
    return text


def truncate_text(text: str, max_words: int) -> str:
    """Truncate text to max words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    
    return ' '.join(words[:max_words]) + '...'


def keyword_in_text(keyword: str, text: str) -> bool:
    """Check if keyword appears in text (case-insensitive, word boundary aware)."""
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def find_keyword_variations(keyword: str) -> List[str]:
    """
    Generate common variations of a keyword.
    
    Example: "JavaScript" -> ["JavaScript", "JS", "javascript", "Java Script"]
    """
    variations = [keyword]
    
    # Lowercase
    variations.append(keyword.lower())
    
    # Common abbreviations
    abbreviations = {
        'javascript': ['JS', 'js'],
        'typescript': ['TS', 'ts'],
        'python': ['py'],
        'kubernetes': ['k8s', 'K8s'],
        'postgresql': ['postgres', 'Postgres', 'psql'],
        'elasticsearch': ['ES', 'elastic'],
        'machine learning': ['ML', 'ml'],
        'artificial intelligence': ['AI', 'ai'],
        'user experience': ['UX', 'ux'],
        'user interface': ['UI', 'ui'],
        'search engine optimization': ['SEO', 'seo'],
        'pay per click': ['PPC', 'ppc'],
        'search engine marketing': ['SEM', 'sem'],
        'continuous integration': ['CI', 'ci'],
        'continuous deployment': ['CD', 'cd'],
        'amazon web services': ['AWS', 'aws'],
        'google cloud platform': ['GCP', 'gcp'],
    }
    
    keyword_lower = keyword.lower()
    if keyword_lower in abbreviations:
        variations.extend(abbreviations[keyword_lower])
    
    # Check if keyword is an abbreviation
    for full, abbrevs in abbreviations.items():
        if keyword_lower in [a.lower() for a in abbrevs]:
            variations.append(full)
            variations.append(full.title())
    
    return list(set(variations))


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple word-based similarity between two texts.
    Returns value between 0 and 1.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)
