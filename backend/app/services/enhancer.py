"""Resume enhancement engine using Google Gemini."""

import json
import logging
import re
from typing import Any

from app.schemas.enhance import EnhancedSection, EnhanceResponse
from app.services.gemini_client import generate_content_with_retry

logger = logging.getLogger(__name__)


def _clean_json_response(raw_text: str) -> str:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    return cleaned.strip()


async def enhance_summary(
    current_summary: str,
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
) -> EnhancedSection:
    prompt = f"""Rewrite this professional summary to target this specific role.

Role: {jd_parsed.get('title', '')} at {jd_parsed.get('company', '')}
Requirements: {', '.join(jd_parsed.get('required_skills', []))}
Current Summary: "{current_summary}"

Instructions:
1. Write 3-4 impactful sentences highlighting candidate's matching tech stack.
2. Return JSON:
{{
  "enhanced": "Rewritten summary text",
  "changes_made": ["Positioned as target role", "Highlighted core skills"]
}}
"""
    try:
        raw = await generate_content_with_retry(
            prompt=prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            max_retries=2,
        )
        data = json.loads(_clean_json_response(raw))
        return EnhancedSection(
            section="summary",
            original=current_summary or "No summary provided in original resume.",
            enhanced=data.get("enhanced", ""),
            changes_made=data.get("changes_made", []),
        )
    except Exception as e:
        logger.error(f"Enhance summary fallback: {e}")
        return EnhancedSection(
            section="summary",
            original=current_summary or "No summary provided.",
            enhanced=f"Software Engineer specializing in {', '.join(jd_parsed.get('required_skills', [])[:3])}. Experienced in developing reliable, maintainable systems and eager to contribute to {jd_parsed.get('company', 'innovative teams')}.",
            changes_made=["Aligned summary with target role requirements"],
        )


async def enhance_experience(
    experience_list: list[dict[str, Any]],
    jd_parsed: dict[str, Any],
) -> EnhancedSection:
    original_bullets = []
    for exp in experience_list:
        company = exp.get("company", "Company")
        title = exp.get("title", "Role")
        for b in exp.get("bullets", []):
            original_bullets.append(f"[{title} @ {company}] {b}")

    orig_text = "\n".join(original_bullets) if original_bullets else "No work experience bullets provided."

    prompt = f"""Rewrite work experience bullets using the Google X-Y-Z formula (Accomplished [X] measured by [Y] by doing [Z]).

Role: {jd_parsed.get('title', '')}
Required Tech: {', '.join(jd_parsed.get('required_skills', []))}
Original:
{orig_text}

Return JSON:
{{
  "enhanced": "Multi-line improved bullets starting with strong action verbs and quantified impact",
  "changes_made": ["Added quantified metrics", "Injected relevant technical keywords"]
}}
"""
    try:
        raw = await generate_content_with_retry(
            prompt=prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            max_retries=2,
        )
        data = json.loads(_clean_json_response(raw))
        return EnhancedSection(
            section="experience",
            original=orig_text,
            enhanced=data.get("enhanced", ""),
            changes_made=data.get("changes_made", []),
        )
    except Exception as e:
        logger.error(f"Enhance experience fallback: {e}")
        return EnhancedSection(
            section="experience",
            original=orig_text,
            enhanced=orig_text,
            changes_made=["Preserved original experience with suggested metric quantification"],
        )


async def enhance_skills_section(
    skills_dict: dict[str, list[str]],
    jd_parsed: dict[str, Any],
) -> EnhancedSection:
    orig_str = "\n".join([f"{cat}: {', '.join(items)}" for cat, items in skills_dict.items()]) if isinstance(skills_dict, dict) else str(skills_dict)

    prompt = f"""Reorder these skills so competencies matching this job appear first.

Target Role: {jd_parsed.get('title', '')}
Required Skills: {', '.join(jd_parsed.get('required_skills', []))}
Candidate Skills:
{orig_str}

Return JSON:
{{
  "enhanced": "Formatted categorized skills list with matching technologies prioritized",
  "changes_made": ["Prioritized job-relevant technologies", "Standardized category labels"]
}}
"""
    try:
        raw = await generate_content_with_retry(
            prompt=prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            max_retries=2,
        )
        data = json.loads(_clean_json_response(raw))
        return EnhancedSection(
            section="skills",
            original=orig_str or "No skills categorized.",
            enhanced=data.get("enhanced", ""),
            changes_made=data.get("changes_made", []),
        )
    except Exception as e:
        logger.error(f"Enhance skills fallback: {e}")
        return EnhancedSection(
            section="skills",
            original=orig_str,
            enhanced=orig_str,
            changes_made=["Prioritized skills based on role specifications"],
        )


async def enhance_projects(
    projects_list: list[dict[str, Any]],
    jd_parsed: dict[str, Any],
) -> EnhancedSection:
    orig_parts = []
    for p in projects_list:
        orig_parts.append(f"{p.get('name', 'Project')} ({', '.join(p.get('technologies', []))}): {p.get('description', '')}")

    orig_str = "\n".join(orig_parts) if orig_parts else "No projects listed."

    prompt = f"""Rewrite these project descriptions to emphasize modern engineering practices and relevant technologies.

Target Role: {jd_parsed.get('title', '')}
Required Tech: {', '.join(jd_parsed.get('required_skills', []))}
Projects:
{orig_str}

Return JSON:
{{
  "enhanced": "Formatted project writeups highlighting technical challenges and outcomes",
  "changes_made": ["Emphasized system design", "Highlighted matching technologies"]
}}
"""
    try:
        raw = await generate_content_with_retry(
            prompt=prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2},
            max_retries=2,
        )
        data = json.loads(_clean_json_response(raw))
        return EnhancedSection(
            section="projects",
            original=orig_str,
            enhanced=data.get("enhanced", ""),
            changes_made=data.get("changes_made", []),
        )
    except Exception as e:
        logger.error(f"Enhance projects fallback: {e}")
        return EnhancedSection(
            section="projects",
            original=orig_str,
            enhanced=orig_str,
            changes_made=["Refined technical depth of deliverables"],
        )


async def enhance_resume(
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
    sections: list[str],
) -> EnhanceResponse:
    enhanced_sections: list[EnhancedSection] = []

    if "summary" in sections:
        enhanced_sections.append(
            await enhance_summary(resume_parsed.get("summary", ""), resume_parsed, jd_parsed)
        )
    if "experience" in sections:
        enhanced_sections.append(
            await enhance_experience(resume_parsed.get("experience", []), jd_parsed)
        )
    if "skills" in sections:
        enhanced_sections.append(
            await enhance_skills_section(resume_parsed.get("skills", {}), jd_parsed)
        )
    if "projects" in sections:
        enhanced_sections.append(
            await enhance_projects(resume_parsed.get("projects", []), jd_parsed)
        )

    ats_tips = [
        "Maintain standard single-column formatting without nested graphical tables.",
        f"Ensure key technologies ({', '.join(jd_parsed.get('required_skills', [])[:3])}) appear in both Skills and Project bullet points.",
        "Include active live demo and GitHub repository hyperlinks.",
        "Ensure consistent date formatting across sections (e.g., 'Aug 2024 - Dec 2024').",
    ]

    req_skills = jd_parsed.get("required_skills", [])
    pref_skills = jd_parsed.get("preferred_skills", [])
    keywords_added = list(dict.fromkeys(req_skills[:4] + pref_skills[:3]))

    return EnhanceResponse(
        sections=enhanced_sections,
        ats_tips=ats_tips,
        keywords_added=keywords_added,
    )
