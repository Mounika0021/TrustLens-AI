
"""
TrustLens AI
Document-Aware Trust Score Calculation

The score considers:
- AI document classification
- AI verification status
- AI confidence
- OCR confidence
- Document-specific validation
- MRZ validation when applicable
"""

from typing import List


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value):
    return bool(value)


def _average_ocr_confidence(ocr_results):
    """
    Calculate average OCR confidence safely.
    """

    if not ocr_results:
        return 0.0

    values = []

    for item in ocr_results:

        if isinstance(item, dict):
            confidence = item.get("confidence", 0.0)

        else:
            confidence = getattr(
                item,
                "confidence",
                0.0
            )

        values.append(
            _safe_float(confidence)
        )

    if not values:
        return 0.0

    return sum(values) / len(values)


def _get_ai_value(ai_result, key, default=None):
    """
    Safely read values from AI result.
    """

    if not ai_result:
        return default

    if isinstance(ai_result, dict):
        return ai_result.get(key, default)

    return getattr(
        ai_result,
        key,
        default
    )


def _get_validation_value(validation, key, default=False):
    """
    Safely read validation values.
    """

    if not validation:
        return default

    if isinstance(validation, dict):
        return validation.get(key, default)

    return getattr(
        validation,
        key,
        default
    )


def calculate_trust_score(
    ocr_results,
    mrz,
    ai_result,
    validation,
):
    """
    Calculate a document-aware trust score.

    Score components:

    AI/document identification       20 points
    AI verification status           25 points
    AI confidence                    20 points
    OCR quality                      20 points
    Validation                       15 points

    Total = 100
    """

    reasons: List[str] = []

    # ==========================================================
    # READ AI RESULT
    # ==========================================================

    document_type = str(
        _get_ai_value(
            ai_result,
            "document_type",
            "Unknown"
        )
    ).strip()

    ai_status = str(
        _get_ai_value(
            ai_result,
            "verification_status",
            "Rejected"
        )
    ).strip()

    ai_confidence = _safe_float(
        _get_ai_value(
            ai_result,
            "confidence",
            0.0
        )
    )

    document_type_lower = document_type.lower()
    ai_status_lower = ai_status.lower()

    # ==========================================================
    # NORMALIZE AI STATUS
    # ==========================================================

    # Some model outputs use "Pass" instead of "Verified".
    if ai_status_lower in {
        "pass",
        "passed",
        "verified",
        "valid"
    }:
        ai_verified = True
    else:
        ai_verified = False

    # ==========================================================
    # 1. DOCUMENT IDENTIFICATION - 20 POINTS
    # ==========================================================

    score = 0

    known_documents = {
        "aadhaar",
        "pan",
        "passport",
        "driving license",
        "driving licence",
        "voter id",
        "voter card",
        "national id",
        "identity card",
    }

    if document_type_lower in known_documents:

        score += 20

        reasons.append(
            f"Document identified as {document_type}."
        )

    elif document_type_lower != "unknown":

        score += 15

        reasons.append(
            f"Document identified as {document_type}."
        )

    else:

        reasons.append(
            "Document type could not be identified."
        )

    # ==========================================================
    # 2. AI VERIFICATION STATUS - 25 POINTS
    # ==========================================================

    if ai_verified:

        score += 25

        reasons.append(
            "AI model classified the document as Verified."
        )

    elif ai_status_lower in {
        "review",
        "needs review",
        "uncertain"
    }:

        score += 10

        reasons.append(
            "AI model recommends document review."
        )

    else:

        reasons.append(
            "AI model did not verify the document."
        )

    # ==========================================================
    # 3. AI CONFIDENCE - 20 POINTS
    # ==========================================================

    ai_confidence = max(
        0.0,
        min(1.0, ai_confidence)
    )

    confidence_points = round(
        ai_confidence * 20
    )

    score += confidence_points

    if ai_confidence >= 0.90:

        reasons.append(
            "High AI confidence."
        )

    elif ai_confidence >= 0.70:

        reasons.append(
            "Moderate AI confidence."
        )

    elif ai_confidence > 0:

        reasons.append(
            "Low AI confidence."
        )

    else:

        reasons.append(
            "No usable AI confidence."
        )

    # ==========================================================
    # 4. OCR QUALITY - 20 POINTS
    # ==========================================================

    avg_ocr = _average_ocr_confidence(
        ocr_results
    )

    avg_ocr = max(
        0.0,
        min(1.0, avg_ocr)
    )

    ocr_points = round(
        avg_ocr * 20
    )

    score += ocr_points

    if not ocr_results:

        reasons.append(
            "No OCR text detected."
        )

    elif avg_ocr >= 0.80:

        reasons.append(
            "High OCR confidence."
        )

    elif avg_ocr >= 0.50:

        reasons.append(
            "Moderate OCR confidence."
        )

    else:

        reasons.append(
            "Low OCR confidence."
        )

    # ==========================================================
    # 5. DOCUMENT-SPECIFIC VALIDATION - 15 POINTS
    # ==========================================================

    # ----------------------------------------------------------
    # PASSPORT / MRZ DOCUMENT
    # ----------------------------------------------------------

    if document_type_lower == "passport":

        passport_ok = _safe_bool(
            _get_validation_value(
                validation,
                "passport_checksum",
                False
            )
        )

        birth_ok = _safe_bool(
            _get_validation_value(
                validation,
                "birth_checksum",
                False
            )
        )

        expiry_ok = _safe_bool(
            _get_validation_value(
                validation,
                "expiry_checksum",
                False
            )
        )

        overall_ok = _safe_bool(
            _get_validation_value(
                validation,
                "overall_checksum",
                False
            )
        )

        checks_passed = sum([
            passport_ok,
            birth_ok,
            expiry_ok,
            overall_ok
        ])

        validation_points = round(
            (checks_passed / 4) * 15
        )

        score += validation_points

        if passport_ok:
            reasons.append(
                "Passport checksum valid."
            )
        else:
            reasons.append(
                "Passport checksum failed."
            )

        if birth_ok:
            reasons.append(
                "Birth date checksum valid."
            )
        else:
            reasons.append(
                "Birth checksum failed."
            )

        if expiry_ok:
            reasons.append(
                "Expiry checksum valid."
            )
        else:
            reasons.append(
                "Expiry checksum failed."
            )

        if overall_ok:
            reasons.append(
                "Overall ICAO checksum valid."
            )
        else:
            reasons.append(
                "Overall checksum failed."
            )

        # AI/OCR MRZ agreement
        similarity = _safe_float(
            _get_validation_value(
                validation,
                "ocr_ai_similarity",
                0.0
            )
        )

        if similarity >= 95:

            reasons.append(
                "AI strongly agrees with OCR MRZ."
            )

        elif similarity >= 80:

            reasons.append(
                "Minor OCR/AI MRZ differences."
            )

        elif similarity > 0:

            reasons.append(
                "OCR and AI MRZ partially disagree."
            )

    # ----------------------------------------------------------
    # NON-MRZ DOCUMENTS
    # ----------------------------------------------------------

    else:

        format_valid = _get_validation_value(
            validation,
            "format_valid",
            None
        )

        if format_valid is True:

            score += 15

            reasons.append(
                f"{document_type} format validation passed."
            )

        else:

            # We do NOT subtract MRZ points from Aadhaar/PAN.
            # These documents do not use passport-style MRZ.
            reasons.append(
                f"MRZ validation not applicable for {document_type}."
            )

            # Give partial validation credit when the AI is
            # highly confident and the document is recognized.
            if (
                document_type_lower != "unknown"
                and ai_verified
                and ai_confidence >= 0.90
            ):

                score += 10

                reasons.append(
                    "Document-specific evidence supports the AI result."
                )

    # ==========================================================
    # FINAL CLAMP
    # ==========================================================

    score = max(
        0,
        min(100, int(score))
    )

    # ==========================================================
    # FINAL STATUS
    # ==========================================================

    if score >= 85:

        status = "Verified"

    elif score >= 65:

        status = "Review"

    else:

        status = "Rejected"

    # Important safety rule:
    # If AI explicitly rejects the document,
    # do not allow a high score to say Verified.

    if not ai_verified and ai_status_lower in {
        "rejected",
        "reject",
        "fail",
        "failed"
    }:

        if score >= 65:
            score = 64

        status = "Rejected"

        reasons.append(
            "Final status capped because AI rejected the document."
        )

    # Unknown document should not be Verified.
    if document_type_lower == "unknown":

        if score >= 65:
            score = 64

        status = "Rejected"

        reasons.append(
            "Unknown document type cannot be automatically verified."
        )

    # ==========================================================
    # RETURN
    # ==========================================================

    return {
        "trust_score": score,
        "status": status,
        "reasons": reasons,
    }
