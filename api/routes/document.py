# ai_detection/api/routes/document.py
"""Document forensic analysis endpoint for TruthLens AI.

Supports PDF files and images. Extracts metadata, performs forensic integrity
checks, generates ELA visualizations for images, and computes SHA-256 hashes.
"""

import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas import DocumentResponse, ErrorResponse

router = APIRouter()

# Maximum document file size: 50 MB
MAX_DOCUMENT_SIZE_BYTES = 50 * 1024 * 1024

# Allowed extensions
ALLOWED_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp", ".gif",
}

# ELA output directory (resolved relative to project root)
_ELA_DIR = Path(__file__).resolve().parents[3] / "outputs" / "api" / "ela"


@router.post(
    "/document",
    response_model=DocumentResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Analyze a document (PDF or image) for forensic metadata and integrity",
)
async def analyze_document_endpoint(file: UploadFile = File(...)):
    """Accept a PDF or image document and return forensic analysis results.

    Extracts metadata, checks integrity indicators, generates ELA for images,
    and computes SHA-256 hash for evidence identification.
    """
    # ── Validate file presence ──────────────────────────────────────
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    # ── Validate extension ──────────────────────────────────────────
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{ext}'. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # ── Read and validate size ──────────────────────────────────────
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > MAX_DOCUMENT_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {MAX_DOCUMENT_SIZE_BYTES // (1024*1024)} MB.",
        )

    # ── Save to temp file with sanitized name ───────────────────────
    safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=ext, prefix="truthlens_doc_"
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # ── Run analysis ────────────────────────────────────────────
        from src.document.analyzer import analyze_document  # noqa: PLC0415

        # Ensure ELA output directory exists
        os.makedirs(str(_ELA_DIR), exist_ok=True)

        result = analyze_document(
            file_path=tmp_path,
            original_filename=file.filename,
            file_size=len(content),
            content_type=file.content_type,
            ela_output_dir=str(_ELA_DIR),
        )

        return DocumentResponse(**result)

    except HTTPException:
        raise  # Re-raise validation errors as-is
    except Exception as e:
        return DocumentResponse(
            status="failed",
            file_info={"filename": file.filename, "file_size_bytes": len(content)},
            message=f"Document analysis failed: {str(e)}",
            warnings=["An unexpected error occurred during analysis."],
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
