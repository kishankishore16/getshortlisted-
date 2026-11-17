"""Unit tests for the hybrid matching and skill extraction engine."""

import pytest
from app.services.matcher import compute_skill_match, compute_fit_score
from app.services.skills import normalize_skill, fuzzy_match_skills
from app.services.scorer import score_completeness, score_impact_language, score_resume


def test_normalize_skill():
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("python3") == "Python"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("postgres") == "PostgreSQL"


def test_fuzzy_match_skills():
    assert fuzzy_match_skills("React", "ReactJS") > 0.7
    assert fuzzy_match_skills("Python", "Python 3") > 0.8
    assert fuzzy_match_skills("Docker", "Kubernetes") < 0.4


def test_compute_skill_match():
    resume_skills = ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "Git"]
    jd_required = ["Python", "FastAPI", "PostgreSQL"]
    jd_preferred = ["Docker", "Kubernetes", "AWS"]

    result = compute_skill_match(resume_skills, jd_required, jd_preferred)
    assert len(result["matched_required"]) == 3
    assert len(result["missing_required"]) == 0
    assert len(result["matched_preferred"]) == 1
    assert "Kubernetes" in result["missing_preferred"]
    assert result["score"] >= 80.0


def test_score_completeness():
    sample_resume = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "summary": "Passionate Software Engineer with 2 years of experience building modern web apps.",
        "education": [{"degree": "B.Tech CSE"}],
        "skills": {"Languages": ["Python", "JavaScript"]},
        "projects": [{"name": "AI App"}],
    }
    score = score_completeness(sample_resume)
    assert score >= 80.0


def test_score_impact_language():
    sample_with_metrics = {
        "experience": [{
            "bullets": [
                "Engineered scalable microservices reducing query latency by 45%.",
                "Spearheaded cloud migration to AWS handling 100k daily requests.",
            ]
        }],
        "projects": [],
    }
    score = score_impact_language(sample_with_metrics)
    assert score >= 60.0


def test_score_resume():
    sample_resume = {
        "name": "Alex Smith",
        "email": "alex@test.com",
        "summary": "Enthusiastic developer focusing on backend systems and microservices.",
        "education": [{"degree": "B.Tech"}],
        "skills": {
            "Languages": ["Python", "Go"],
            "Databases": ["PostgreSQL", "Redis"],
            "Cloud": ["Docker", "AWS"],
        },
        "projects": [{"name": "Cache Service", "description": "High throughput key-value store", "bullets": ["Engineered with Go"]}],
        "experience": [],
    }
    result = score_resume(sample_resume)
    assert result.overall_score > 60.0
    assert len(result.tips) > 0
