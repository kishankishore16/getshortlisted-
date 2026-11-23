"""Resume parsing pipeline using PyMuPDF for PDF extraction and Gemini for structured parsing."""

import json
import logging
import re

import pymupdf as fitz

from app.schemas.resume import ParsedResume
from app.services.gemini_client import generate_content_with_retry

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text content from a PDF file.

    Uses PyMuPDF (fitz) to open the PDF from bytes and extract text
    from every page, concatenated with newlines.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        The extracted plain text from the PDF.

    Raises:
        ValueError: If the PDF cannot be opened or contains no text.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts: list[str] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)

        doc.close()

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            raise ValueError("PDF contains no extractable text. Scanned images are not supported.")

        return full_text

    except fitz.FileDataError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")


async def parse_resume_with_llm(text: str) -> dict:
    """Parse resume text into structured data using Google Gemini.

    Sends the extracted resume text to Gemini with a detailed prompt
    instructing it to return a JSON object matching the ParsedResume schema.

    Args:
        text: The raw text extracted from the resume PDF.

    Returns:
        A dictionary containing the parsed resume fields.
    """
    # Truncate text if excessively long to prevent token overflow and latency
    truncated_text = text[:8000]

    prompt = f"""You are an expert resume parser. Analyze the following resume text and extract structured information.

Return a valid JSON object with EXACTLY these fields (use empty strings or empty arrays if information is not found):

{{
    "name": "Full name of the candidate",
    "email": "Email address",
    "phone": "Phone number",
    "location": "City, State/Country",
    "linkedin": "LinkedIn profile URL",
    "github": "GitHub profile URL",
    "portfolio": "Portfolio/personal website URL",
    "summary": "Professional summary or objective statement",
    "education": [
        {{
            "institution": "University/College name",
            "degree": "Degree type (e.g., B.Tech, M.S.)",
            "field_of_study": "Major/Field",
            "start_date": "Start date",
            "end_date": "End date or 'Present'",
            "gpa": "GPA if mentioned",
            "description": "Any additional details"
        }}
    ],
    "skills": {{
        "Programming Languages": ["skill1", "skill2"],
        "Frameworks & Libraries": ["skill1"],
        "Databases & Tools": ["skill1"]
    }},
    "experience": [
        {{
            "company": "Company name",
            "title": "Job title",
            "location": "Location",
            "start_date": "Start date",
            "end_date": "End date",
            "description": "Role overview",
            "bullets": ["Action verb bullet point with metrics"]
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "What it does",
            "technologies": ["tech1", "tech2"],
            "url": "Project link if any",
            "bullets": ["Technical achievement"]
        }}
    ],
    "certifications": [
        {{
            "name": "Certification name",
            "issuer": "Issuing organization",
            "date": "Issue date",
            "url": "Credential URL if any"
        }}
    ]
}}

CRITICAL INSTRUCTIONS:
1. Extract ALL skills listed and group them logically.
2. Return ONLY the raw JSON object. Do not include markdown codeblocks, explanation, or notes.

RESUME TEXT:
{truncated_text}
"""

    raw_response = await generate_content_with_retry(
        prompt=prompt,
        generation_config={"response_mime_type": "application/json", "temperature": 0.1},
        max_retries=3,
    )

    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_response.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        parsed_data = json.loads(cleaned)
        if isinstance(parsed_data, dict):
            return parsed_data
        raise ValueError("Response was not a JSON object")
    except Exception as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}. Raw response: {raw_response[:300]}")
        raise RuntimeError(f"AI response format error: {str(e)}")


async def parse_resume(file_bytes: bytes) -> ParsedResume:
    """Full resume parsing pipeline: PDF extraction -> LLM structuring."""
    raw_text = extract_text_from_pdf(file_bytes)
    parsed_dict = await parse_resume_with_llm(raw_text)

    try:
        return ParsedResume.model_validate(parsed_dict)
    except Exception as e:
        logger.warning(f"Pydantic validation fallback: {e}")
        return ParsedResume(
            name=parsed_dict.get("name", ""),
            email=parsed_dict.get("email", ""),
            phone=parsed_dict.get("phone", ""),
            location=parsed_dict.get("location", ""),
            linkedin=parsed_dict.get("linkedin", ""),
            github=parsed_dict.get("github", ""),
            portfolio=parsed_dict.get("portfolio", ""),
            summary=parsed_dict.get("summary", ""),
            skills=parsed_dict.get("skills", {}),
            education=parsed_dict.get("education", []),
            experience=parsed_dict.get("experience", []),
            projects=parsed_dict.get("projects", []),
            certifications=parsed_dict.get("certifications", []),
        )
