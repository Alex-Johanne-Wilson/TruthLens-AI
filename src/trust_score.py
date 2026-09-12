# ai_detection/src/trust_score.py
"""TruthLens AI — Unified Trust Score Aggregator (PROTOTYPE).

This module implements a rule-based evidence aggregator that combines
available forensic analysis results into a single trust assessment.

IMPORTANT: This is a PROTOTYPE implementation. The scoring methodology
has not been scientifically validated and should be clearly communicated
as an approximate heuristic, not a calibrated forensic metric.
"""

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Evidence weight configuration
# ---------------------------------------------------------------------------
# Each module contributes a weighted score. Only modules that actually
# produced results are included in the denominator.
MODULE_WEIGHTS = {
    "ai_image_detection": 0.30,
    "deepfake_detection": 0.15,
    "metadata_analysis": 0.20,
    "ela_analysis": 0.15,
    "document_forensics": 0.20,
}


def compute_trust_score(
    image_result: Optional[Dict[str, Any]] = None,
    deepfake_result: Optional[Dict[str, Any]] = None,
    document_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute a unified trust score from available evidence.

    Parameters
    ----------
    image_result : dict, optional
        Response from /api/analyze/image (ImageResponse fields).
    deepfake_result : dict, optional
        Response from /api/analyze/deepfake (DeepFakeResponse fields).
    document_result : dict, optional
        Response from /api/analyze/document (DocumentResponse fields).

    Returns
    -------
    dict
        Trust assessment containing score, evidence breakdown, and warnings.
    """
    evidence_items: List[Dict[str, Any]] = []
    warnings: List[str] = []
    modules_used: List[str] = []
    modules_unavailable: List[str] = []
    total_weight = 0.0
    weighted_sum = 0.0

    # ── AI Image Detection ──────────────────────────────────────────
    if image_result:
        real_prob = float(image_result.get("real_probability", 0.0))
        confidence = float(image_result.get("confidence", 0.0))
        predicted = image_result.get("predicted_class", "unknown")

        # Score: how much the evidence supports authenticity (0-100)
        if predicted == "real":
            module_score = real_prob * 100
        else:
            module_score = (1 - confidence) * 100  # Low trust if classified as AI

        weight = MODULE_WEIGHTS["ai_image_detection"]
        weighted_sum += module_score * weight
        total_weight += weight
        modules_used.append("AI Image Detection (EfficientNet-B0)")

        evidence_items.append({
            "module": "AI Image Detection",
            "verdict": predicted,
            "confidence": round(confidence * 100, 1),
            "trust_contribution": round(module_score, 1),
            "weight": f"{weight * 100:.0f}%",
            "status": "evaluated",
        })
    else:
        modules_unavailable.append("AI Image Detection")

    # ── Deepfake Detection ──────────────────────────────────────────
    if deepfake_result:
        model_ready = deepfake_result.get("model_ready", False)
        status = deepfake_result.get("status", "unknown")

        if model_ready and status == "completed":
            real_prob = float(deepfake_result.get("real_probability", 0.0))
            prediction = deepfake_result.get("overall_prediction", "unknown")

            if prediction == "likely_real":
                module_score = real_prob * 100
            elif prediction == "likely_fake":
                module_score = (1 - real_prob) * 100
                module_score = max(0, 100 - module_score)  # Invert: low trust for fake
            else:
                module_score = 50.0  # Inconclusive = neutral

            weight = MODULE_WEIGHTS["deepfake_detection"]
            weighted_sum += module_score * weight
            total_weight += weight
            modules_used.append("Deepfake Video Detection (ResNet-18)")

            evidence_items.append({
                "module": "Deepfake Detection",
                "verdict": prediction,
                "confidence": round(float(deepfake_result.get("confidence_score", 0)) * 100, 1),
                "trust_contribution": round(module_score, 1),
                "weight": f"{weight * 100:.0f}%",
                "status": "evaluated",
            })
        else:
            modules_unavailable.append("Deepfake Detection (model not ready)")
            warnings.append("Deepfake model is not trained — excluded from trust score.")
            evidence_items.append({
                "module": "Deepfake Detection",
                "verdict": "unavailable",
                "confidence": 0,
                "trust_contribution": 0,
                "weight": f"{MODULE_WEIGHTS['deepfake_detection'] * 100:.0f}%",
                "status": "model_not_ready",
            })
    else:
        modules_unavailable.append("Deepfake Detection")

    # ── Document / Metadata Analysis ────────────────────────────────
    if document_result:
        doc_status = document_result.get("status", "unknown")
        forensic_indicators = document_result.get("forensic_indicators", [])
        metadata = document_result.get("metadata", {})

        if doc_status in ("completed", "partial"):
            # Score based on indicator severity
            warning_count = sum(1 for i in forensic_indicators if i.get("severity") == "warning")
            error_count = sum(1 for i in forensic_indicators if i.get("severity") == "error")

            # Start at 80 (neutral positive), deduct for warnings/errors
            module_score = max(0, 80 - (warning_count * 15) - (error_count * 30))

            # Bonus for having rich metadata (suggests unaltered)
            if metadata.get("exif") or metadata.get("document_info"):
                module_score = min(100, module_score + 10)

            weight = MODULE_WEIGHTS["metadata_analysis"]
            weighted_sum += module_score * weight
            total_weight += weight
            modules_used.append("Document & Metadata Forensics")

            evidence_items.append({
                "module": "Document & Metadata Analysis",
                "verdict": f"{len(forensic_indicators)} indicators found",
                "confidence": 0,  # Not a model-based confidence
                "trust_contribution": round(module_score, 1),
                "weight": f"{weight * 100:.0f}%",
                "status": "evaluated",
            })

            # ELA
            ela_path = document_result.get("ela_path")
            if ela_path:
                ela_weight = MODULE_WEIGHTS["ela_analysis"]
                # ELA alone can't determine trust — contribute a neutral score
                ela_score = 60.0
                weighted_sum += ela_score * ela_weight
                total_weight += ela_weight
                modules_used.append("Error Level Analysis (ELA)")

                evidence_items.append({
                    "module": "Error Level Analysis",
                    "verdict": "generated",
                    "confidence": 0,
                    "trust_contribution": round(ela_score, 1),
                    "weight": f"{ela_weight * 100:.0f}%",
                    "status": "evaluated",
                    "note": "ELA is an indicator only — visual inspection required",
                })
        else:
            modules_unavailable.append("Document Analysis (analysis failed)")
    else:
        modules_unavailable.append("Document & Metadata Analysis")

    # ── Compute final score ─────────────────────────────────────────
    if total_weight > 0:
        # Normalize by actual weight used (not total possible weight)
        raw_score = weighted_sum / total_weight
        trust_score = round(max(0, min(100, raw_score)), 1)
    else:
        trust_score = None  # No evidence available

    # ── Determine overall assessment ────────────────────────────────
    if trust_score is None:
        assessment = "no_evidence"
        assessment_label = "No Evidence Available"
    elif trust_score >= 80:
        assessment = "likely_authentic"
        assessment_label = "Likely Authentic"
    elif trust_score >= 60:
        assessment = "possibly_authentic"
        assessment_label = "Possibly Authentic — Some Concerns"
    elif trust_score >= 40:
        assessment = "inconclusive"
        assessment_label = "Inconclusive — Insufficient or Mixed Evidence"
    elif trust_score >= 20:
        assessment = "possibly_manipulated"
        assessment_label = "Possibly Manipulated — Significant Concerns"
    else:
        assessment = "likely_manipulated"
        assessment_label = "Likely Manipulated"

    # Coverage: what fraction of possible evidence was used
    coverage = round((total_weight / sum(MODULE_WEIGHTS.values())) * 100, 1) if total_weight > 0 else 0.0

    # General warning
    warnings.append(
        "This trust score is a PROTOTYPE heuristic aggregation. "
        "It has not been scientifically validated and should not be used "
        "as the sole basis for forensic determinations."
    )

    return {
        "trust_score": trust_score,
        "assessment": assessment,
        "assessment_label": assessment_label,
        "evidence_coverage": coverage,
        "evidence_breakdown": evidence_items,
        "modules_used": modules_used,
        "modules_unavailable": modules_unavailable,
        "warnings": warnings,
        "methodology": "PROTOTYPE — Rule-based weighted evidence aggregation",
    }
