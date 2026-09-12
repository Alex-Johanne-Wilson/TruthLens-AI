# ai_detection/src/document/analyzer.py
"""Document forensic analysis module for TruthLens AI.

Provides metadata extraction, integrity checks, ELA, and hash generation
for PDF documents and images submitted as evidence.
"""

import hashlib
import io
import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ExifTags

# PDF support — optional import
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_TEXT_EXTRACT_CHARS = 2000
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp", ".gif"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS

# ELA quality level used for re-saving
ELA_QUALITY = 90
ELA_AMPLIFICATION = 15  # Multiplier to amplify differences


# ---------------------------------------------------------------------------
# File utilities
# ---------------------------------------------------------------------------

def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def detect_document_type(file_path: str, content_type: Optional[str] = None) -> str:
    """Determine whether file is a PDF, image, or unknown."""
    ext = Path(file_path).suffix.lower()
    if ext in SUPPORTED_PDF_EXTENSIONS:
        return "pdf"
    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    # Fallback: check MIME
    if content_type:
        if "pdf" in content_type:
            return "pdf"
        if content_type.startswith("image/"):
            return "image"
    return "unknown"


def get_file_info(file_path: str, original_filename: str, file_size: int) -> Dict[str, Any]:
    """Build basic file information dict."""
    ext = Path(original_filename).suffix.lower()
    mime, _ = mimetypes.guess_type(original_filename)
    return {
        "filename": original_filename,
        "extension": ext,
        "mime_type": mime or "unknown",
        "file_size_bytes": file_size,
        "file_size_human": _human_size(file_size),
    }


def _human_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


# ---------------------------------------------------------------------------
# PDF Analysis
# ---------------------------------------------------------------------------

def extract_pdf_metadata(file_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Optional[str]]:
    """Extract metadata, forensic indicators, and text from a PDF file.

    Returns (metadata_dict, forensic_indicators_list, extracted_text).
    """
    if not HAS_PYPDF2:
        return (
            {"error": "PyPDF2 not installed — PDF analysis unavailable"},
            [{"severity": "info", "category": "dependency", "description": "PyPDF2 is not installed. Install with: pip install PyPDF2"}],
            None,
        )

    metadata: Dict[str, Any] = {}
    indicators: List[Dict[str, Any]] = []
    text_content = ""

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            # Basic PDF info
            metadata["page_count"] = len(reader.pages)
            metadata["is_encrypted"] = reader.is_encrypted

            # Document info / metadata
            info = reader.metadata
            if info:
                raw_meta = {}
                for key in ["/Title", "/Author", "/Creator", "/Producer",
                            "/CreationDate", "/ModDate", "/Subject", "/Keywords"]:
                    val = info.get(key)
                    if val:
                        raw_meta[key.strip("/")] = str(val)
                metadata["document_info"] = raw_meta

                # Parse dates for anomaly checks
                creation = raw_meta.get("CreationDate")
                modification = raw_meta.get("ModDate")
                if creation and modification:
                    _check_date_anomalies(creation, modification, indicators)

                # Check for editing software
                producer = raw_meta.get("Producer", "")
                creator = raw_meta.get("Creator", "")
                if producer or creator:
                    _check_editing_software(producer, creator, indicators)
            else:
                metadata["document_info"] = {}
                indicators.append({
                    "severity": "info",
                    "category": "metadata",
                    "description": "No document metadata found in PDF. Metadata may have been stripped.",
                })

            # Encryption check
            if reader.is_encrypted:
                indicators.append({
                    "severity": "warning",
                    "category": "security",
                    "description": "PDF is encrypted. Some analysis may be limited.",
                })

            # Extract text from first few pages
            try:
                pages_to_extract = min(5, len(reader.pages))
                for i in range(pages_to_extract):
                    page_text = reader.pages[i].extract_text() or ""
                    text_content += page_text + "\n"
                text_content = text_content[:MAX_TEXT_EXTRACT_CHARS].strip()
            except Exception:
                text_content = None

            # Check for embedded files / attachments
            try:
                if "/Names" in reader.trailer.get("/Root", {}):
                    indicators.append({
                        "severity": "info",
                        "category": "structure",
                        "description": "PDF contains named objects (may include embedded files).",
                    })
            except Exception:
                pass

    except Exception as e:
        metadata["error"] = f"Failed to parse PDF: {str(e)}"
        indicators.append({
            "severity": "error",
            "category": "parsing",
            "description": f"PDF parsing error: {str(e)}",
        })

    return metadata, indicators, text_content if text_content else None


def _check_date_anomalies(creation: str, modification: str, indicators: list):
    """Check for suspicious date patterns in PDF metadata."""
    try:
        # PDF dates are often in format D:YYYYMMDDHHmmSS
        c_clean = creation.replace("D:", "").replace("'", "")[:14]
        m_clean = modification.replace("D:", "").replace("'", "")[:14]

        if len(c_clean) >= 8 and len(m_clean) >= 8:
            c_date = datetime.strptime(c_clean[:8], "%Y%m%d")
            m_date = datetime.strptime(m_clean[:8], "%Y%m%d")

            if m_date < c_date:
                indicators.append({
                    "severity": "warning",
                    "category": "timestamp",
                    "description": (
                        f"Modification date ({m_date.date()}) is BEFORE creation date ({c_date.date()}). "
                        "This is unusual and may indicate timestamp manipulation."
                    ),
                })

            # Check for future dates
            now = datetime.now()
            if c_date > now or m_date > now:
                indicators.append({
                    "severity": "warning",
                    "category": "timestamp",
                    "description": "Document contains future date(s) in metadata, which is suspicious.",
                })
    except (ValueError, IndexError):
        pass  # Date format not parseable — not an anomaly itself


def _check_editing_software(producer: str, creator: str, indicators: list):
    """Note any editing software detected in metadata."""
    software = producer or creator
    indicators.append({
        "severity": "info",
        "category": "software",
        "description": f"Document produced by: {software}",
    })


# ---------------------------------------------------------------------------
# Image EXIF Analysis
# ---------------------------------------------------------------------------

def extract_image_metadata(file_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Extract EXIF metadata and forensic indicators from an image.

    Returns (metadata_dict, forensic_indicators_list).
    """
    metadata: Dict[str, Any] = {}
    indicators: List[Dict[str, Any]] = []

    try:
        img = Image.open(file_path)
        metadata["format"] = img.format
        metadata["mode"] = img.mode
        metadata["width"] = img.width
        metadata["height"] = img.height
        metadata["dimensions"] = f"{img.width} x {img.height}"

        # EXIF data
        exif_data = {}
        raw_exif = img.getexif()
        if raw_exif:
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                # Convert non-serializable types
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="replace")
                    except Exception:
                        value = f"<binary {len(value)} bytes>"
                elif isinstance(value, tuple):
                    value = str(value)
                exif_data[tag_name] = str(value)

            metadata["exif"] = exif_data

            # Extract key fields
            metadata["camera_make"] = exif_data.get("Make", "Not available")
            metadata["camera_model"] = exif_data.get("Model", "Not available")
            metadata["software"] = exif_data.get("Software", "Not available")
            metadata["datetime_original"] = exif_data.get("DateTimeOriginal",
                                            exif_data.get("DateTime", "Not available"))
            metadata["orientation"] = exif_data.get("Orientation", "Not available")

            # GPS presence check
            gps_ifd = raw_exif.get_ifd(ExifTags.IFD.GPSInfo) if hasattr(ExifTags, 'IFD') else {}
            if gps_ifd:
                metadata["gps_present"] = True
                indicators.append({
                    "severity": "info",
                    "category": "geolocation",
                    "description": "GPS coordinates found in image metadata.",
                })
            else:
                metadata["gps_present"] = False

            # Software editing check
            software = exif_data.get("Software", "")
            if software and software != "Not available":
                indicators.append({
                    "severity": "info",
                    "category": "software",
                    "description": f"Image processed/created with: {software}",
                })
        else:
            metadata["exif"] = {}
            indicators.append({
                "severity": "info",
                "category": "metadata",
                "description": (
                    "No EXIF metadata found. This is common for screenshots, "
                    "web-downloaded images, or images with stripped metadata."
                ),
            })

        img.close()

    except Exception as e:
        metadata["error"] = f"Failed to read image: {str(e)}"
        indicators.append({
            "severity": "error",
            "category": "parsing",
            "description": f"Image parsing error: {str(e)}",
        })

    return metadata, indicators


# ---------------------------------------------------------------------------
# Error Level Analysis (ELA)
# ---------------------------------------------------------------------------

def perform_ela(file_path: str, output_dir: str, quality: int = ELA_QUALITY) -> Optional[str]:
    """Perform Error Level Analysis on a JPEG/PNG image.

    Re-saves the image at a lower JPEG quality and computes pixel-level
    differences. Regions that have been modified tend to show higher error
    levels than unmodified regions.

    Returns the relative URL path to the ELA image, or None if ELA failed.
    """
    try:
        original = Image.open(file_path).convert("RGB")

        # Re-save at lower quality to a buffer
        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer).convert("RGB")

        # Compute pixel-level difference
        orig_arr = np.array(original, dtype=np.float32)
        resaved_arr = np.array(resaved, dtype=np.float32)

        diff = np.abs(orig_arr - resaved_arr)
        # Amplify the differences for visibility
        diff = np.clip(diff * ELA_AMPLIFICATION, 0, 255).astype(np.uint8)

        ela_image = Image.fromarray(diff)

        # Save ELA output
        os.makedirs(output_dir, exist_ok=True)
        stem = Path(file_path).stem
        ela_filename = f"ela_{stem}.png"
        ela_path = os.path.join(output_dir, ela_filename)
        ela_image.save(ela_path)

        original.close()
        resaved.close()

        return f"/static/ela/{ela_filename}"

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main Document Analyzer
# ---------------------------------------------------------------------------

def analyze_document(
    file_path: str,
    original_filename: str,
    file_size: int,
    content_type: Optional[str] = None,
    ela_output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run full document forensic analysis pipeline.

    Parameters
    ----------
    file_path : str
        Path to the uploaded file on disk.
    original_filename : str
        Original filename from the upload.
    file_size : int
        Size of the file in bytes.
    content_type : str, optional
        MIME type from the upload.
    ela_output_dir : str, optional
        Directory to save ELA output images.

    Returns
    -------
    dict
        Complete analysis result matching DocumentResponse schema.
    """
    result: Dict[str, Any] = {
        "status": "completed",
        "file_info": get_file_info(file_path, original_filename, file_size),
        "document_type": "unknown",
        "metadata": {},
        "forensic_indicators": [],
        "text_extract": None,
        "sha256_hash": None,
        "ela_path": None,
        "warnings": [],
        "message": "",
    }

    # SHA-256 hash
    try:
        result["sha256_hash"] = compute_sha256(file_path)
    except Exception as e:
        result["warnings"].append(f"Could not compute SHA-256: {str(e)}")

    # Determine document type
    doc_type = detect_document_type(file_path, content_type)
    result["document_type"] = doc_type

    if doc_type == "pdf":
        metadata, indicators, text = extract_pdf_metadata(file_path)
        result["metadata"] = metadata
        result["forensic_indicators"].extend(indicators)
        result["text_extract"] = text
        result["message"] = f"PDF analysis completed. {len(indicators)} forensic indicator(s) found."

    elif doc_type == "image":
        metadata, indicators = extract_image_metadata(file_path)
        result["metadata"] = metadata
        result["forensic_indicators"].extend(indicators)
        result["message"] = f"Image metadata analysis completed. {len(indicators)} forensic indicator(s) found."

        # Perform ELA for images
        if ela_output_dir:
            ela_url = perform_ela(file_path, ela_output_dir)
            if ela_url:
                result["ela_path"] = ela_url
                result["forensic_indicators"].append({
                    "severity": "info",
                    "category": "ela",
                    "description": (
                        "Error Level Analysis (ELA) image generated. ELA highlights regions "
                        "with different compression levels, which MAY indicate editing. "
                        "Note: ELA is an indicator, not definitive proof of manipulation."
                    ),
                })

    else:
        result["status"] = "partial"
        result["message"] = f"Unsupported document type: {Path(original_filename).suffix}. Only basic file info and hash available."
        result["warnings"].append("Document format not fully supported for forensic analysis.")

    # Always add general disclaimer
    result["warnings"].append(
        "Metadata anomalies alone do not prove tampering. "
        "Forensic indicators should be corroborated with additional evidence."
    )

    return result
