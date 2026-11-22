"""Job description parsing service using Google Gemini."""

import json
import logging
import re

from app.services.gemini_client import generate_content_with_retry

logger = logging.getLogger(__name__)

# Patterns to detect JD source platforms
_SOURCE_PATTERNS: list[tuple[str, str]] = [
    (r"linkedin\.com", "LinkedIn"),
    (r"naukri\.com", "Naukri"),
    (r"indeed\.com", "Indeed"),
    (r"glassdoor\.com", "Glassdoor"),
    (r"angel\.co|wellfound\.com", "AngelList"),
    (r"lever\.co", "Lever"),
    (r"greenhouse\.io", "Greenhouse"),
    (r"workday\.com", "Workday"),
    (r"internshala\.com", "Internshala"),
    (r"unstop\.com", "Unstop"),
]


def detect_source_hint(jd_text: str) -> str | None:
    text_lower = jd_text.lower()
    for pattern, source_name in _SOURCE_PATTERNS:
        if re.search(pattern, text_lower):
            return source_name
    return None


async def parse_jd_with_llm(jd_text: str) -> dict:
    truncated_jd = jd_text[:8000]

    prompt = f"""You are an expert technical recruiter. Parse the following job description into structured information.

Return a valid JSON object with EXACTLY these fields:
{{
    "title": "Exact job title",
    "company": "Company name",
    "required_skills": ["Mandatory technical skill 1", "Skill 2"],
    "preferred_skills": ["Good to have skill 1", "Skill 2"],
    "experience_level": "e.g. 0-2 years, Fresher, Entry Level",
    "responsibilities": ["Primary job duty 1", "Primary job duty 2"],
    "qualifications": ["Degree requirements, e.g. B.Tech Computer Science"]
}}

CRITICAL INSTRUCTIONS:
1. Normalize and extract concrete programming languages, frameworks, cloud tools, databases.
2. Return ONLY the raw JSON object.

JOB DESCRIPTION:
{truncated_jd}
"""

    raw_response = await generate_content_with_retry(
        prompt=prompt,
        generation_config={"response_mime_type": "application/json", "temperature": 0.1},
        max_retries=3,
    )

    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_response.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
        raise ValueError("Response was not a JSON object")
    except Exception as e:
        logger.error(f"Failed to parse JD JSON: {e}")
        return {
            "title": "Software Engineer",
            "company": "Target Company",
            "required_skills": ["Python", "JavaScript", "SQL", "Git"],
            "preferred_skills": ["Docker", "AWS", "React"],
            "experience_level": "Entry Level",
            "responsibilities": ["Design and implement scalable software features"],
            "qualifications": ["Bachelor's in Computer Science or related engineering degree"],
        }
