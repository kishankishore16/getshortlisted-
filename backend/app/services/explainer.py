"""LLM Explanation service using Google Gemini."""

import json
import logging
import re
from typing import Any

from app.services.gemini_client import generate_content_with_retry

logger = logging.getLogger(__name__)


def _clean_json_response(raw_text: str) -> str:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    return cleaned.strip()


async def generate_fit_explanation(
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
    score_breakdown: dict[str, Any],
) -> str:
    prompt = f"""You are a technical career mentor and hiring advisor.
Explain why this candidate matches this role, citing their specific skills, projects, and strengths.

Score Breakdown:
- Overall: {score_breakdown.get('overall')}%
- Semantic Alignment: {score_breakdown.get('semantic_similarity')}%
- Skill Match: {score_breakdown.get('skill_match')}%
- Experience Fit: {score_breakdown.get('experience_alignment')}%

Target Role: {jd_parsed.get('title', 'Software Engineer')} at {jd_parsed.get('company', 'Target Company')}
Required Skills: {', '.join(jd_parsed.get('required_skills', []))}

Candidate Summary: {resume_parsed.get('summary', '')}
Candidate Skills: {json.dumps(resume_parsed.get('skills', {}))}
Candidate Projects: {json.dumps(resume_parsed.get('projects', []))}

Write a 3-4 sentence professional evaluation addressing the candidate directly ('You').
Highlight matching capabilities and technical synergy with the job requirements. Output plain text without markdown."""

    try:
        text = await generate_content_with_retry(prompt=prompt, max_retries=2)
        return text if text else "Your technical foundation demonstrates strong alignment with the role's core requirements."
    except Exception as e:
        logger.error(f"Fit explanation fallback: {e}")
        return f"Your technical background aligns well with the {jd_parsed.get('title', 'role')} position, meeting key requirements in {', '.join(jd_parsed.get('required_skills', ['software development'])[:3])}."


async def generate_missing_skills(
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
    skill_match: dict[str, Any],
) -> list[dict[str, Any]]:
    missing_required = skill_match.get("missing_required", [])
    missing_preferred = skill_match.get("missing_preferred", [])

    if not missing_required and not missing_preferred:
        return []

    # Limit to top 6 skills to speed up processing and prevent quota exhaustion
    req_slice = missing_required[:4]
    pref_slice = missing_preferred[:3]

    prompt = f"""You are an engineering career mentor.
Create an actionable learning path for these missing skills for a {jd_parsed.get('title', 'Engineering')} role at {jd_parsed.get('company', 'Company')}:

Missing Required: {json.dumps(req_slice)}
Missing Preferred: {json.dumps(pref_slice)}

Return a valid JSON array:
[
  {{
    "skill_name": "Skill Name",
    "priority": "required" or "preferred",
    "reason": "Why this skill is needed in 1 concise sentence",
    "estimated_learning_time": "e.g. 3-5 days or 1-2 weeks",
    "resources": [
      "https://official-docs-or-tutorial-url",
      "https://freecodecamp-or-youtube-url"
    ]
  }}
]
Return ONLY the raw JSON array."""

    try:
        raw_res = await generate_content_with_retry(
            prompt=prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            max_retries=2,
        )
        cleaned = _clean_json_response(raw_res)
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except Exception as e:
        logger.error(f"Missing skills fallback: {e}")

    # Fallback
    fallback = []
    for s in req_slice:
        fallback.append({
            "skill_name": s,
            "priority": "required",
            "reason": f"Core requirement for everyday duties at {jd_parsed.get('company', 'this company')}.",
            "estimated_learning_time": "1-2 weeks",
            "resources": [
                f"https://devdocs.io/{s.lower().replace(' ', '-')}",
                f"https://www.freecodecamp.org/news/search/?query={s.replace(' ', '%20')}",
            ],
        })
    for s in pref_slice:
        fallback.append({
            "skill_name": s,
            "priority": "preferred",
            "reason": "Helpful differentiator that elevates your candidate profile.",
            "estimated_learning_time": "3-5 days",
            "resources": [
                "https://roadmap.sh",
                f"https://www.youtube.com/results?search_query={s.replace(' ', '+')}+crash+course",
            ],
        })
    return fallback


async def generate_keyword_analysis(
    resume_text: str,
    jd_text: str,
    jd_parsed: dict[str, Any],
) -> dict[str, Any]:
    prompt = f"""You are an ATS optimization specialist.
Identify keywords found in both the resume and JD, and critical missing keywords.

Job: {jd_parsed.get('title', '')}
JD Excerpt: {jd_text[:2000]}
Resume Excerpt: {resume_text[:2000]}

Return a valid JSON object:
{{
  "keywords_in_both": ["keyword1", "keyword2"],
  "keywords_missing_from_resume": ["missing1", "missing2"],
  "keywords_to_add": [
    {{
      "keyword": "string",
      "suggested_placement": "e.g. Technical Skills section or Projects section"
    }}
  ]
}}
Return ONLY the raw JSON object."""

    try:
        raw_res = await generate_content_with_retry(
            prompt=prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            max_retries=2,
        )
        cleaned = _clean_json_response(raw_res)
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Keyword analysis fallback: {e}")
        req = jd_parsed.get("required_skills", [])
        pref = jd_parsed.get("preferred_skills", [])
        return {
            "keywords_in_both": req[:3],
            "keywords_missing_from_resume": pref[:3],
            "keywords_to_add": [
                {"keyword": k, "suggested_placement": "Technical Skills & Project bullets"}
                for k in pref[:3]
            ],
        }
