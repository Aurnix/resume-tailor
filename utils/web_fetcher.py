"""
Web Fetcher - Extracts job descriptions from URLs.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse


# Common job board selectors
JOB_CONTENT_SELECTORS = [
    # Lever
    '.posting-headline',
    '.posting-categories', 
    '.section-wrapper',
    
    # Greenhouse
    '#app_body',
    '.job__description',
    '#content',
    
    # Workday
    '.job-posting-section',
    '.WOTC',
    
    # LinkedIn
    '.show-more-less-html__markup',
    '.description__text',
    
    # Indeed
    '#jobDescriptionText',
    '.jobsearch-jobDescriptionText',
    
    # Generic
    '.job-description',
    '.job-details',
    '[data-testid="job-description"]',
    '.description',
    'article',
    'main',
]


def fetch_job_posting(url: str, timeout: int = 30) -> str:
    """
    Fetch and extract job description from URL.
    
    Args:
        url: Job posting URL
        timeout: Request timeout in seconds
    
    Returns:
        Extracted job description text
    """
    
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    
    # Fetch page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch URL: {e}")
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()
    
    # Try job-specific selectors first
    for selector in JOB_CONTENT_SELECTORS:
        elements = soup.select(selector)
        if elements:
            text = '\n\n'.join(el.get_text(separator='\n', strip=True) for el in elements)
            if len(text) > 200:  # Likely found real content
                return clean_job_text(text)
    
    # Fallback: extract all text from body
    body = soup.find('body')
    if body:
        text = body.get_text(separator='\n', strip=True)
        return clean_job_text(text)
    
    return clean_job_text(soup.get_text(separator='\n', strip=True))


def clean_job_text(text: str) -> str:
    """Clean extracted job description text."""
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\t+', ' ', text)
    
    # Remove common cruft
    patterns_to_remove = [
        r'Apply Now.*',
        r'Share this job.*',
        r'Save this job.*',
        r'Similar Jobs.*',
        r'Report this job.*',
        r'Cookie Settings.*',
        r'Privacy Policy.*',
        r'Terms of Service.*',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Trim leading/trailing whitespace
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    return text.strip()


def extract_company_from_url(url: str) -> Optional[str]:
    """Try to extract company name from job URL."""
    
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Known patterns
    patterns = {
        'lever.co': lambda u: u.split('/')[3] if len(u.split('/')) > 3 else None,
        'greenhouse.io': lambda u: u.split('/')[3] if len(u.split('/')) > 3 else None,
        'jobs.ashbyhq.com': lambda u: u.split('/')[3] if len(u.split('/')) > 3 else None,
    }
    
    for pattern, extractor in patterns.items():
        if pattern in domain:
            try:
                return extractor(url)
            except:
                pass
    
    # Try domain name
    parts = domain.replace('www.', '').replace('jobs.', '').replace('careers.', '').split('.')
    if parts:
        return parts[0].title()
    
    return None


def is_job_url(url: str) -> bool:
    """Check if URL looks like a job posting."""
    
    job_indicators = [
        'lever.co',
        'greenhouse.io',
        'ashbyhq.com',
        'workday.com',
        'jobs.',
        'careers.',
        '/jobs/',
        '/careers/',
        '/job/',
        '/position/',
        '/opening/',
        'linkedin.com/jobs',
        'indeed.com/viewjob',
    ]
    
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in job_indicators)
