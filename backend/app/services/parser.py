"""Resume parsing pipeline using PyMuPDF for PDF extraction and Gemini for structured parsing."""

import json
import logging

import fitz  # PyMuPDF
import google.generativeai as genai

from app.config import settings
from app.schemas.resume import ParsedResume

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


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
            raise ValueError("PDF contains no extractable text.")

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

    Raises:
        RuntimeError: If Gemini fails to return valid JSON.
    """
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
        "Category Name": ["skill1", "skill2"]
    }},
    "experience": [
        {{
            "company": "Company name",
            "title": "Job title",
            "location": "Job location",
            "start_date": "Start date",
            "end_date": "End date or 'Present'",
            "description": "Brief role description",
            "bullets": ["Achievement/responsibility bullet point 1", "bullet 2"]
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"],
            "url": "Project URL if any",
            "bullets": ["Key detail 1", "Key detail 2"]
        }}
    ],
    "certifications": [
        {{
            "name": "Certification name",
            "issuer": "Issuing organization",
            "date": "Date obtained",
            "url": "Certificate URL if any"
        }}
    ]
}}

IMPORTANT RULES:
1. Extract skills and group them into logical categories (e.g., "Programming Languages", "Frameworks", "Databases", "Tools", "Soft Skills").
2. For experience bullets, preserve the original wording as much as possible.
3. If a section is not present in the resume, use empty arrays/strings.
4. Return ONLY the JSON object, no markdown formatting, no code blocks, no extra text.
5. Ensure all JSON is valid and properly escaped.

RESUME TEXT:
{text}
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

            parsed_data: dict = json.loads(response_text)
            return parsed_data

        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON for resume parsing: {e}")
            raise RuntimeError(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            logger.warning(f"Gemini resume parsing attempt {attempt + 1} with {chosen_model} failed: {e}")
            if ("429" in str(e) or "503" in str(e) or "404" in str(e)) and attempt < 2:
                import asyncio
                await asyncio.sleep(2)
                continue
            if attempt == 2:
                raise RuntimeError(f"Resume parsing with Gemini failed: {str(e)}")


async def parse_resume(file_bytes: bytes) -> ParsedResume:
    """Full resume parsing pipeline: PDF extraction → LLM structuring.

    Orchestrates the complete resume parsing process by first extracting
    text from the PDF, then sending it to Gemini for structured parsing,
    and finally validating the result against the ParsedResume schema.

    Args:
        file_bytes: Raw bytes of the uploaded PDF resume file.

    Returns:
        A validated ParsedResume Pydantic model instance.

    Raises:
        ValueError: If the PDF is invalid or empty.
        RuntimeError: If the LLM parsing fails.
    """
    # Step 1: Extract text from PDF
    raw_text = extract_text_from_pdf(file_bytes)
    logger.info(f"Extracted {len(raw_text)} characters from resume PDF.")

    # Step 2: Parse with LLM
    parsed_dict = await parse_resume_with_llm(raw_text)

    # Step 3: Validate against schema (Pydantic will fill defaults for missing fields)
    try:
        parsed_resume = ParsedResume.model_validate(parsed_dict)
    except Exception as e:
        logger.warning(f"Pydantic validation had issues, using raw dict: {e}")
        # Attempt graceful fallback — construct with what we have
        parsed_resume = ParsedResume(
            name=parsed_dict.get("name", ""),
            email=parsed_dict.get("email", ""),
            phone=parsed_dict.get("phone", ""),
            location=parsed_dict.get("location", ""),
            linkedin=parsed_dict.get("linkedin", ""),
            github=parsed_dict.get("github", ""),
            portfolio=parsed_dict.get("portfolio", ""),
            summary=parsed_dict.get("summary", ""),
            skills=parsed_dict.get("skills", {}),
        )

    return parsed_resume
