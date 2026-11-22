"""Centralized Google Gemini helper with model fallbacks, retry logic, and rate-limit handling."""

import asyncio
import logging
from typing import Any

import google.generativeai as genai

from app.config import settings

logger = logging.getLogger(__name__)

# Fallback sequence of models
MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
]

_initialized = False


def ensure_gemini_init():
    """Ensure Gemini API is configured once settings are loaded."""
    global _initialized
    if not _initialized:
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _initialized = True
            logger.info("Google Gemini client initialized successfully.")
        else:
            logger.warning("GEMINI_API_KEY is not set.")


async def generate_content_with_retry(
    prompt: str,
    generation_config: dict[str, Any] | None = None,
    max_retries: int = 3,
) -> str:
    """Generate content from Gemini with automatic exponential backoff and model fallbacks.

    Args:
        prompt: Prompt string.
        generation_config: Optional GenerationConfig dict.
        max_retries: Number of retry attempts.

    Returns:
        Generated text string.
    """
    ensure_gemini_init()

    last_error: Exception | None = None

    for attempt in range(max_retries):
        model_name = MODELS[attempt % len(MODELS)]
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
                f"Gemini call to {model_name} failed (attempt {attempt + 1}/{max_retries}): {e}"
            )
            
            # Rate limit or quota exhaustion: backoff
            if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                wait_time = 2.0 * (attempt + 1)
                logger.info(f"Rate limit hit. Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(1.0)

    raise RuntimeError(f"All Gemini model attempts failed. Last error: {last_error}")
