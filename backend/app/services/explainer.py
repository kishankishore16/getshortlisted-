"""LLM Explanation service using Google Gemini 2.0 Flash.

Generates natural language explanations of match strength, actionable skill-gap
learning paths, and ATS keyword optimization analysis.
"""

import json
import logging
import re
from typing import Any

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)


def _clean_json_response(raw_text: str) -> str:
    """Strip markdown code fence wrappers from LLM output."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    return cleaned.strip()


async def generate_fit_explanation(
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
    score_breakdown: dict[str, Any],
) -> str:
    """Generate a 3-5 sentence natural language explanation of candidate fit.

    Args:
        resume_parsed: Parsed resume data.
        jd_parsed: Parsed job description.
        score_breakdown: ScoreBreakdown dict.

    Returns:
        Clear, encouraging, yet honest explanation paragraph.
    """
    prompt = f"""You are an elite campus tech recruiter and career coach.
Explain why this student candidate is a good fit for this role, referencing their specific projects, skills, or experience.

Score Breakdown:
- Overall Fit: {score_breakdown.get('overall')}%
- Semantic Similarity: {score_breakdown.get('semantic_similarity')}%
- Skill Match: {score_breakdown.get('skill_match')}%
- Experience Alignment: {score_breakdown.get('experience_alignment')}%

Job: {jd_parsed.get('title', 'Software Engineer')} at {jd_parsed.get('company', 'Target Company')}
Required Skills: {', '.join(jd_parsed.get('required_skills', []))}
Preferred Skills: {', '.join(jd_parsed.get('preferred_skills', []))}

Candidate Summary: {resume_parsed.get('summary', '')}
Candidate Skills: {json.dumps(resume_parsed.get('skills', {}))}
Candidate Experience: {json.dumps(resume_parsed.get('experience', []))}
Candidate Projects: {json.dumps(resume_parsed.get('projects', []))}

Provide a direct, inspiring 3-5 sentence paragraph addressing the student directly ('You').
Highlight 2-3 specific strengths, acknowledge how their projects or tech stack align with the JD, and summarize their competitive advantage.
Do not use markdown headers or bullet points. Output only the plain paragraph."""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        return text if text else "You have a solid foundation with matching technical skills and relevant project experience for this role."
    except Exception as e:
        logger.error(f"Error generating fit explanation: {e}")
        return (
            f"Your technical background aligns well with the {jd_parsed.get('title', 'role')} position. "
            f"Your key skills and project portfolio demonstrate practical hands-on capability for the responsibilities listed."
        )


async def generate_missing_skills(
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
    skill_match: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate actionable skill gap breakdown with learning resources.

    Args:
        resume_parsed: Parsed candidate resume.
        jd_parsed: Parsed JD.
        skill_match: Output of compute_skill_match.

    Returns:
        List of dicts with skill_name, priority, reason, estimated_learning_time, resources.
    """
    missing_required = skill_match.get("missing_required", [])
    missing_preferred = skill_match.get("missing_preferred", [])

    if not missing_required and not missing_preferred:
        return []

    prompt = f"""You are a technical career mentor for software engineers.
A student is missing the following skills required/preferred for a {jd_parsed.get('title', 'Software Engineering')} role at {jd_parsed.get('company', 'the company')}.

Missing Required Skills: {json.dumps(missing_required)}
Missing Preferred Skills: {json.dumps(missing_preferred)}

Candidate Current Skills: {json.dumps(resume_parsed.get('skills', {}))}

Return a valid JSON array of objects with this schema for each missing skill:
[
  {{
    "skill_name": "Skill Name",
    "priority": "required" or "preferred",
    "reason": "Why this specific skill is critical for this role in 1-2 concise sentences",
    "estimated_learning_time": "e.g. 3-5 days or 1-2 weeks",
    "resources": [
      "https://official-docs-or-tutorial-url",
      "https://freecodecamp-or-youtube-url"
    ]
  }}
]

Output ONLY the JSON array. Do not add markdown explanation."""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = await model.generate_content_async(prompt)
        cleaned = _clean_json_response(response.text)
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except Exception as e:
        logger.error(f"Error generating missing skills guidance: {e}")

    # Fallback default items
    fallback_gaps = []
    for skill in missing_required:
        fallback_gaps.append({
            "skill_name": skill,
            "priority": "required",
            "reason": f"Essential core requirement for daily duties at {jd_parsed.get('company', 'this company')}.",
            "estimated_learning_time": "1-2 weeks",
            "resources": [
                f"https://devdocs.io/{skill.lower().replace(' ', '-')}",
                "https://www.freecodecamp.org/news/search/?query=" + skill.replace(" ", "%20"),
            ],
        })
    for skill in missing_preferred:
        fallback_gaps.append({
            "skill_name": skill,
            "priority": "preferred",
            "reason": "Valuable differentiator that puts you ahead of other candidates.",
            "estimated_learning_time": "3-5 days",
            "resources": [
                "https://roadmap.sh",
                "https://www.youtube.com/results?search_query=" + skill.replace(" ", "+") + "+crash+course",
            ],
        })
    return fallback_gaps


async def generate_keyword_analysis(
    resume_text: str,
    jd_text: str,
    jd_parsed: dict[str, Any],
) -> dict[str, Any]:
    """Identify matching and missing keywords for ATS optimization.

    Args:
        resume_text: Raw or formatted candidate text.
        jd_text: Raw job description text.
        jd_parsed: Parsed JD.

    Returns:
        Dict with keywords_in_both, keywords_missing_from_resume, and keywords_to_add with placement advice.
    """
    prompt = f"""You are an ATS (Applicant Tracking System) optimization expert.
Analyze the resume and job description to identify keyword matches and gaps.

Job Title: {jd_parsed.get('title', '')}
Job Description Excerpt:
{jd_text[:2500]}

Candidate Resume Text:
{resume_text[:2500]}

Return a valid JSON object with EXACTLY this structure:
{{
  "keywords_in_both": ["keyword1", "keyword2", "keyword3"],
  "keywords_missing_from_resume": ["missingKeyword1", "missingKeyword2"],
  "keywords_to_add": [
    {{
      "keyword": "string",
      "suggested_placement": "e.g. Summary section or Projects section bullet"
    }}
  ]
}}

Ensure high-value technical keywords, methodologies (e.g., Agile, CI/CD, Microservices), and domain terms are captured.
Output ONLY the JSON object."""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = await model.generate_content_async(prompt)
        cleaned = _clean_json_response(response.text)
        return json.loads(cleaned)
    except Exception as e:
        logger.error(f"Error in keyword analysis: {e}")
        return {
            "keywords_in_both": jd_parsed.get("required_skills", [])[:3],
            "keywords_missing_from_resume": jd_parsed.get("preferred_skills", [])[:3],
            "keywords_to_add": [
                {"keyword": k, "suggested_placement": "Skills / Projects section"}
                for k in jd_parsed.get("preferred_skills", [])[:3]
            ],
        }
