"""Standalone resume quality scoring service.

Evaluates resume quality independently without needing a job description,
assessing completeness, action verb usage, metrics quantification,
technical keyword density, and formatting clarity.
"""

import logging
import re
from typing import Any

from app.schemas.resume import ResumeQualityScore

logger = logging.getLogger(__name__)

ACTION_VERBS = {
    "accelerated", "achieved", "analyzed", "architected", "automated",
    "built", "collaborated", "constructed", "decreased", "delivered",
    "designed", "developed", "devised", "engineered", "established",
    "executed", "expanded", "generated", "implemented", "improved",
    "increased", "initiated", "launched", "led", "managed", "maximized",
    "minimized", "modeled", "optimized", "orchestrated", "refactored",
    "reduced", "resolved", "revamped", "scaled", "simplified", "spearheaded",
    "streamlined", "supervised", "trained", "transformed", "upgraded"
}


def score_completeness(parsed: dict[str, Any]) -> float:
    """Check presence of essential resume sections (0-100)."""
    score = 0.0
    if parsed.get("name"):
        score += 10.0
    if parsed.get("email") or parsed.get("phone"):
        score += 10.0
    if parsed.get("summary") and len(parsed.get("summary", "").strip()) > 30:
        score += 15.0
    if parsed.get("education") and len(parsed.get("education", [])) > 0:
        score += 20.0
    if parsed.get("skills") and any(len(v) > 0 for v in parsed.get("skills", {}).values()):
        score += 25.0
    if parsed.get("projects") and len(parsed.get("projects", [])) > 0:
        score += 15.0
    if parsed.get("experience") and len(parsed.get("experience", [])) > 0:
        score += 5.0
    return min(100.0, score)


def score_impact_language(parsed: dict[str, Any]) -> float:
    """Measure presence of action verbs and quantified impact/metrics."""
    all_text = []
    for exp in parsed.get("experience", []):
        all_text.extend(exp.get("bullets", []))
    for proj in parsed.get("projects", []):
        all_text.extend(proj.get("bullets", []))
        all_text.append(proj.get("description", ""))

    combined = " ".join(all_text).lower()
    if not combined.strip():
        return 35.0

    words = re.findall(r"\b[a-z]+\b", combined)
    if not words:
        return 35.0

    # Count action verbs
    verb_matches = sum(1 for w in words if w in ACTION_VERBS)
    verb_score = min(50.0, (verb_matches / 6.0) * 50.0)

    # Count numbers / percentages / metrics
    numbers = re.findall(r"\b\d+(?:[\.,]\d+)?%?|\b\d+k\b|\b\d+x\b", combined)
    metric_score = min(50.0, (len(numbers) / 4.0) * 50.0)

    return round(verb_score + metric_score, 1)


def score_keyword_richness(parsed: dict[str, Any]) -> float:
    """Measure depth and categorization of technical skills."""
    skills_dict = parsed.get("skills", {})
    total_skills = sum(len(items) for items in skills_dict.values()) if isinstance(skills_dict, dict) else 0

    if total_skills >= 15:
        score = 95.0
    elif total_skills >= 10:
        score = 80.0
    elif total_skills >= 6:
        score = 65.0
    elif total_skills >= 1:
        score = 45.0
    else:
        score = 20.0

    # Bonus if skills are categorized into 3+ groups
    if isinstance(skills_dict, dict) and len(skills_dict) >= 3:
        score = min(100.0, score + 10.0)

    return round(score, 1)


def score_structure(parsed: dict[str, Any]) -> float:
    """Evaluate structural organization and section balance."""
    score = 60.0
    if parsed.get("linkedin") or parsed.get("github"):
        score += 15.0
    if parsed.get("certifications") and len(parsed.get("certifications", [])) > 0:
        score += 10.0
    # Balanced projects
    projects = parsed.get("projects", [])
    if 2 <= len(projects) <= 4:
        score += 15.0
    return min(100.0, score)


def score_specificity(parsed: dict[str, Any]) -> float:
    """Detect whether descriptions cite specific technologies rather than generic terms."""
    vague_phrases = ["worked on", "handled", "helped with", "responsible for", "assisted", "did tasks"]
    all_bullets = []
    for exp in parsed.get("experience", []):
        all_bullets.extend(exp.get("bullets", []))
    for proj in parsed.get("projects", []):
        all_bullets.extend(proj.get("bullets", []))

    text = " ".join(all_bullets).lower()
    if not text:
        return 50.0

    vague_count = sum(1 for p in vague_phrases if p in text)
    deduction = min(40.0, vague_count * 10.0)
    base = 90.0 - deduction
    return round(max(30.0, min(100.0, base)), 1)


def score_resume(parsed: dict[str, Any]) -> ResumeQualityScore:
    """Compute overall resume score and generate concrete improvement tips."""
    comp = score_completeness(parsed)
    impact = score_impact_language(parsed)
    kw = score_keyword_richness(parsed)
    struct = score_structure(parsed)
    spec = score_specificity(parsed)

    # Weighted calculation
    overall = (
        comp * 0.25
        + impact * 0.25
        + kw * 0.20
        + struct * 0.15
        + spec * 0.15
    )
    overall_clamped = round(min(100.0, max(0.0, overall)), 1)

    tips: list[str] = []
    if impact < 70.0:
        tips.append("Quantify your achievements using specific numbers, percentages, or scale metrics in project bullet points.")
        tips.append("Start each bullet point with high-impact action verbs (e.g. 'Engineered', 'Optimized', 'Architected').")
    if kw < 70.0:
        tips.append("Expand your Technical Skills section into defined categories (Languages, Frameworks, Cloud, Databases).")
    if not parsed.get("github") and not parsed.get("linkedin"):
        tips.append("Include clickable links to your GitHub profile and LinkedIn to demonstrate proof of work.")
    if comp < 80.0 and not parsed.get("summary"):
        tips.append("Add a targeted 2-3 sentence professional summary at the top outlining your engineering focus.")
    if spec < 70.0:
        tips.append("Avoid passive phrases like 'worked on' or 'helped with'; clearly state your specific individual contribution.")

    if not tips:
        tips.append("Excellent resume structure! Keep project bullets updated with your latest deployed applications.")

    return ResumeQualityScore(
        overall_score=overall_clamped,
        completeness=round(comp, 1),
        impact_language=round(impact, 1),
        keyword_richness=round(kw, 1),
        structure=round(struct, 1),
        specificity=round(spec, 1),
        tips=tips,
    )
