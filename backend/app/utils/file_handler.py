"""File handling utilities for Cloudinary upload."""

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.config import settings


def _configure_cloudinary() -> None:
    """Configure the Cloudinary SDK from the CLOUDINARY_URL setting.

    The CLOUDINARY_URL has the format:
        cloudinary://api_key:api_secret@cloud_name
    Cloudinary's SDK can parse this automatically.
    """
    cloudinary.config(
        cloudinary_url=settings.CLOUDINARY_URL,
        secure=True,
    )


# Configure on module import
_configure_cloudinary()


async def upload_to_cloudinary(file: UploadFile) -> str:
    """Upload a file to Cloudinary and return its secure URL.

    Reads the uploaded file content, sends it to Cloudinary's upload API
    under the 'getshortlisted/resumes' folder, and returns the public URL.

    Args:
        file: The FastAPI UploadFile object from the request.

    Returns:
        The secure URL string of the uploaded file on Cloudinary.

    Raises:
        HTTPException: 400 if the file is not a PDF.
        HTTPException: 500 if the Cloudinary upload fails.
    """
    if file.content_type and file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    try:
        file_content = await file.read()

        result = cloudinary.uploader.upload(
            file_content,
            folder="getshortlisted/resumes",
            resource_type="raw",
            format="pdf",
        )

        url: str = result.get("secure_url", result.get("url", ""))
        if not url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cloudinary upload returned no URL.",
            )

        return url

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to Cloudinary: {str(e)}",
        )
