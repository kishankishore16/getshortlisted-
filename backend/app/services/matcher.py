"""Hybrid matching engine for resume-to-job matching.

Combines semantic similarity, normalized skill overlap, experience alignment,
and education qualifications into an explainable 0-100 fit score.
"""

import logging
from typing import Any

from app.schemas.analysis import ScoreBreakdown
from app.services.embeddings import compute_similarity
from app.services.skills import fuzzy_match_skills, normalize_skill

logger = logging.getLogger(__name__)


def extract_flat_skills(skills_data: dict[str, list[str]] | list[str] | Any) -> list[str]:
    """Helper to flatten any skill dictionary or list into a clean list of strings."""
    flat_skills: list[str] = []
    if isinstance(skills_data, dict):
        for category, skill_list in skills_data.items():
            if isinstance(skill_list, list):
                for s in skill_list:
                    if isinstance(s, str) and s.strip():
                        flat_skills.append(s.strip())
    elif isinstance(skills_data, list):
        for s in skills_data:
            if isinstance(s, str) and s.strip():
                flat_skills.append(s.strip())
            elif isinstance(s, dict) and "name" in s:
                flat_skills.append(str(s["name"]).strip())
    return flat_skills


def compute_skill_match(
    resume_skills: list[str],
    jd_required: list[str],
    jd_preferred: list[str],
) -> dict[str, Any]:
    """Compute matched and missing skills between candidate and JD requirements.

    Uses canonical normalization and fuzzy matching (>0.8 threshold).

    Args:
        resume_skills: List of candidate skills.
        jd_required: List of mandatory job skills.
        jd_preferred: List of nice-to-have job skills.

    Returns:
        Dict with matched_required, matched_preferred, missing_required,
        missing_preferred, and overall skill_score (0-100).
    """
    normalized_resume = {normalize_skill(s).lower(): s for s in resume_skills if s}

    matched_required: list[dict[str, str]] = []
    missing_required: list[str] = []

    matched_preferred: list[dict[str, str]] = []
    missing_preferred: list[str] = []

    def match_against_resume(target_skill: str) -> str | None:
        canonical_target = normalize_skill(target_skill).lower()
        if canonical_target in normalized_resume:
            return normalized_resume[canonical_target]
        for res_norm, orig_res in normalized_resume.items():
            if fuzzy_match_skills(canonical_target, res_norm) >= 0.8:
                return orig_res
            if canonical_target in res_norm or res_norm in canonical_target:
                return orig_res
        return None

    for req in jd_required:
        matched_as = match_against_resume(req)
        if matched_as:
            matched_required.append({"jd_skill": req, "resume_match": matched_as})
        else:
            missing_required.append(req)

    for pref in jd_preferred:
        matched_as = match_against_resume(pref)
        if matched_as:
            matched_preferred.append({"jd_skill": pref, "resume_match": matched_as})
        else:
            missing_preferred.append(pref)

    total_req = len(jd_required)
    total_pref = len(jd_preferred)

    req_score = (len(matched_required) / total_req) if total_req > 0 else 1.0
    pref_score = (len(matched_preferred) / total_pref) if total_pref > 0 else 1.0

    # 75% weight on required skills, 25% on preferred
    if total_req > 0 and total_pref > 0:
        composite_skill_score = (req_score * 0.75 + pref_score * 0.25) * 100.0
    elif total_req > 0:
        composite_skill_score = req_score * 100.0
    elif total_pref > 0:
        composite_skill_score = pref_score * 100.0
    else:
        composite_skill_score = 75.0

    return {
        "matched_required": matched_required,
        "matched_preferred": matched_preferred,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
        "score": round(min(100.0, max(0.0, composite_skill_score)), 1),
    }


def compute_experience_alignment(
    resume_experience: list[dict[str, Any]],
    resume_projects: list[dict[str, Any]],
    jd_responsibilities: list[str],
) -> float:
    """Compute semantic alignment between candidate work/projects and job duties.

    Args:
        resume_experience: Candidate's past roles & bullets.
        resume_projects: Candidate's projects & descriptions.
        jd_responsibilities: Responsibilities listed in the JD.

    Returns:
        Score between 0.0 and 100.0.
    """
    if not jd_responsibilities:
        return 75.0

    candidate_text_chunks: list[str] = []
    for exp in resume_experience:
        title = exp.get("title", "")
        company = exp.get("company", "")
        bullets = " ".join(exp.get("bullets", []))
        candidate_text_chunks.append(f"{title} at {company}: {bullets}")

    for proj in resume_projects:
        name = proj.get("name", "")
        desc = proj.get("description", "")
        bullets = " ".join(proj.get("bullets", []))
        tech = " ".join(proj.get("technologies", []))
        candidate_text_chunks.append(f"Project {name} ({tech}): {desc} {bullets}")

    candidate_exp_text = " ".join(candidate_text_chunks)
    if not candidate_exp_text.strip():
        return 45.0  # Freshers / students with minimal experience

    jd_resp_text = " ".join(jd_responsibilities)
    sim = compute_similarity(candidate_exp_text, jd_resp_text)
    # Scale from cosine similarity (typically 0.3-0.8) to a realistic 0-100 score
    scaled = (sim - 0.2) / 0.6 * 100.0
    return round(min(100.0, max(20.0, scaled)), 1)


def compute_education_fit(
    resume_education: list[dict[str, Any]],
    jd_qualifications: list[str],
) -> float:
    """Compute candidate's degree and field alignment with JD requirements.

    Args:
        resume_education: Education list.
        jd_qualifications: Qualifications listed in JD.

    Returns:
        Score between 0.0 and 100.0.
    """
    if not resume_education:
        return 60.0
    if not jd_qualifications:
        return 85.0

    edu_str = " ".join([
        f"{e.get('degree', '')} {e.get('field_of_study', '')} {e.get('institution', '')}"
        for e in resume_education
    ]).lower()

    qual_str = " ".join(jd_qualifications).lower()

    # Look for relevant degrees / CS keywords
    keywords = ["b.tech", "btech", "b.e", "computer science", "information technology", "bca", "mca", "b.s", "engineering"]
    matches = sum(1 for kw in keywords if kw in edu_str and (kw in qual_str or "degree" in qual_str or "bachelor" in qual_str))

    base_score = 75.0 + min(25.0, matches * 10.0)
    return round(min(100.0, base_score), 1)


def compute_fit_score(
    resume_parsed: dict[str, Any],
    jd_parsed: dict[str, Any],
    resume_raw_text: str = "",
    jd_raw_text: str = "",
) -> ScoreBreakdown:
    """Run full hybrid scoring engine.

    Weights:
      40% Semantic Similarity (Embeddings)
      35% Skill Match (Normalized keyword & fuzzy)
      15% Experience Alignment
      10% Education Fit

    Returns:
        ScoreBreakdown instance with component scores and overall score.
    """
    # 1. Semantic Similarity
    if not resume_raw_text:
        resume_raw_text = str(resume_parsed)
    if not jd_raw_text:
        jd_raw_text = str(jd_parsed)

    raw_sim = compute_similarity(resume_raw_text, jd_raw_text)
    semantic_score = round(min(100.0, max(20.0, ((raw_sim - 0.25) / 0.55) * 100.0)), 1)

    # 2. Skill Match
    skills_extracted = extract_flat_skills(resume_parsed.get("skills", {}))
    jd_req = jd_parsed.get("required_skills", [])
    jd_pref = jd_parsed.get("preferred_skills", [])
    skill_res = compute_skill_match(skills_extracted, jd_req, jd_pref)
    skill_score = skill_res["score"]

    # 3. Experience Alignment
    exp = resume_parsed.get("experience", [])
    proj = resume_parsed.get("projects", [])
    responsibilities = jd_parsed.get("responsibilities", [])
    exp_score = compute_experience_alignment(exp, proj, responsibilities)

    # 4. Education Fit
    edu = resume_parsed.get("education", [])
    quals = jd_parsed.get("qualifications", [])
    edu_score = compute_education_fit(edu, quals)

    # Weighted sum
    overall = (
        semantic_score * 0.40
        + skill_score * 0.35
        + exp_score * 0.15
        + edu_score * 0.10
    )
    overall_clamped = round(min(100.0, max(0.0, overall)), 1)

    return ScoreBreakdown(
        semantic_similarity=semantic_score,
        skill_match=skill_score,
        experience_alignment=exp_score,
        education_fit=edu_score,
        overall=overall_clamped,
    )
