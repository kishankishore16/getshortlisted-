"""Job description parsing service using Google Gemini.

Extracts structured data from raw job description text, including
required/preferred skills, experience level, and responsibilities.
"""

import json
import logging
import re

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

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
    (r"monster\.com", "Monster"),
    (r"ziprecruiter\.com", "ZipRecruiter"),
    (r"dice\.com", "Dice"),
    (r"stackoverflow\.com|stackoverflowbusiness", "Stack Overflow"),
    (r"internshala\.com", "Internshala"),
    (r"unstop\.com", "Unstop"),
]


def detect_source_hint(jd_text: str) -> str | None:
    """Detect the source platform from patterns in the JD text.

    Scans the job description text for known platform URL patterns
    and returns the platform name if found.

    Args:
        jd_text: The raw job description text.

    Returns:
        The detected platform name, or None if no pattern matched.
    """
    text_lower = jd_text.lower()
    for pattern, source_name in _SOURCE_PATTERNS:
        if re.search(pattern, text_lower):
            return source_name
    return None


async def parse_jd_with_llm(jd_text: str) -> dict:
    """Parse a job description into structured data using Google Gemini.

    Sends the raw JD text to Gemini with a detailed prompt to extract
    the job title, company, required/preferred skills, experience level,
    responsibilities, and qualifications.

    Args:
        jd_text: The raw job description text.

    Returns:
        A dictionary containing the parsed JD fields:
        - title: str
        - company: str
        - required_skills: list[str]
        - preferred_skills: list[str]
        - experience_level: str
        - min_experience_years: int | None
        - max_experience_years: int | None
        - responsibilities: list[str]
        - qualifications: list[str]
        - location: str
        - job_type: str (e.g., "Full-time", "Internship")

    Raises:
        RuntimeError: If Gemini fails to return valid JSON.
    """
    prompt = f"""You are an expert job description parser. Analyze the following job description and extract structured information.

Return a valid JSON object with EXACTLY these fields:

{{
    "title": "Job title",
    "company": "Company name",
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["nice-to-have skill1", "nice-to-have skill2"],
    "experience_level": "Entry Level / Junior / Mid-Level / Senior / Lead / Principal",
    "min_experience_years": null,
    "max_experience_years": null,
    "responsibilities": ["responsibility 1", "responsibility 2"],
    "qualifications": ["qualification 1", "qualification 2"],
    "location": "Job location or 'Remote'",
    "job_type": "Full-time / Part-time / Contract / Internship"
}}

IMPORTANT RULES:
1. Clearly distinguish between REQUIRED skills (must-have) and PREFERRED skills (nice-to-have).
2. Extract individual skills, not categories. E.g., "Python" not "Programming Languages".
3. If experience years are mentioned (e.g., "3-5 years"), set min_experience_years=3, max_experience_years=5.
4. For qualifications, include education requirements and any certifications mentioned.
5. Return ONLY the JSON object, no markdown formatting, no code blocks.
6. If any field is not found, use empty string or empty array.

JOB DESCRIPTION TEXT:
{jd_text}
"""

    candidate_models = [settings.GEMINI_MODEL, "gemini-3.5-flash-lite", "gemini-3.5-flash"]
    models_to_try = list(dict.fromkeys([m for m in candidate_models if m]))

    for attempt in range(3):
        chosen_model = models_to_try[attempt % len(models_to_try)]
        try:
            model = genai.GenerativeModel(chosen_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            response_text = response.text.strip()

            # Clean up potential markdown code blocks
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                response_text = "\n".join(lines)

            parsed_jd: dict = json.loads(response_text)

            # Ensure required keys exist with defaults
            parsed_jd.setdefault("title", "")
            parsed_jd.setdefault("company", "")
            parsed_jd.setdefault("required_skills", [])
            parsed_jd.setdefault("preferred_skills", [])
            parsed_jd.setdefault("experience_level", "")
            parsed_jd.setdefault("min_experience_years", None)
            parsed_jd.setdefault("max_experience_years", None)
            parsed_jd.setdefault("responsibilities", [])
            parsed_jd.setdefault("qualifications", [])
            parsed_jd.setdefault("location", "")
            parsed_jd.setdefault("job_type", "")

            return parsed_jd

        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON for JD parsing: {e}")
            raise RuntimeError(f"Failed to parse Gemini JD response as JSON: {str(e)}")
        except Exception as e:
            logger.warning(f"Gemini JD parsing attempt {attempt + 1} with {chosen_model} failed: {e}")
            if ("429" in str(e) or "503" in str(e) or "404" in str(e)) and attempt < 2:
                import asyncio
                await asyncio.sleep(2)
                continue
            if attempt == 2:
                raise RuntimeError(f"JD parsing with Gemini failed: {str(e)}")
