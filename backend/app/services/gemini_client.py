"""Centralized Google Gemini helper with model fallbacks, retry logic, and rate-limit handling."""

import asyncio
import logging
from typing import Any

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore

from app.config import settings

logger = logging.getLogger(__name__)

# Fallback sequence of current active Gemini models
DEFAULT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]

_initialized = False


def ensure_gemini_init():
    """Ensure Gemini API is configured once settings are loaded."""
    global _initialized
    if not _initialized:
        if genai is None:
            raise RuntimeError("google-generativeai is not installed in the python environment.")
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _initialized = True
            logger.info("Google Gemini client initialized successfully.")
        else:
            logger.warning("GEMINI_API_KEY is not set.")


def get_model_sequence() -> list[str]:
    """Build deduplicated candidate model sequence prioritizing configured model."""
    preferred = settings.GEMINI_MODEL.strip() if settings.GEMINI_MODEL else ""
    raw_list = [preferred] + DEFAULT_MODELS if preferred else DEFAULT_MODELS
    seen = set()
    result = []
    for m in raw_list:
        if m and m not in seen:
            seen.add(m)
            result.append(m)
    return result


async def generate_content_with_retry(
    prompt: str,
    generation_config: dict[str, Any] | None = None,
    max_retries: int | None = None,
) -> str:
    """Generate content from Gemini with automatic exponential backoff and model fallbacks.

    Args:
        prompt: Prompt string.
        generation_config: Optional GenerationConfig dict.
        max_retries: Number of retry attempts. Defaults to the number of available models.

    Returns:
        Generated text string.
    """
    ensure_gemini_init()

    models = get_model_sequence()
    total_attempts = max_retries if max_retries is not None else len(models)
    total_attempts = max(total_attempts, len(models))

    last_error: Exception | None = None

    for attempt in range(total_attempts):
        model_name = models[attempt % len(models)]
        try:
            model = genai.GenerativeModel(model_name)

            # Run in threadpool to prevent blocking asyncio event loop
            loop = asyncio.get_event_loop()

            if generation_config:
                gen_config = genai.GenerationConfig(**generation_config)
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt, generation_config=gen_config)
                )
            else:
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(prompt)
                )

            if response and response.text:
                return response.text.strip()
            raise ValueError(f"Empty response from {model_name}")

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            logger.warning(
                f"Gemini call to {model_name} failed (attempt {attempt + 1}/{total_attempts}): {e}"
            )

            # If 404 or model not found / no longer available, switch to next model immediately
            if "404" in err_str or "not found" in err_str or "no longer available" in err_str:
                logger.info(f"Model {model_name} unavailable; immediately trying next candidate model...")
                continue

            # Rate limit or quota exhaustion: exponential backoff
            if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                wait_time = 2.0 * (attempt + 1)
                logger.info(f"Rate limit hit on {model_name}. Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(0.5)

    raise RuntimeError(f"All Gemini model attempts failed. Last error: {last_error}")
