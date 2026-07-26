"""
TrustLens AI
Trust Score Calculation
"""

from typing import List


def calculate_trust_score(
    ocr_results,
    mrz,
    ai_result,
    validation,
):
    """
    Calculate trust score based on:
    - OCR confidence
    - ICAO validation
    - AI agreement
    """

    score = 100
    reasons: List[str] = []

    # --------------------------
    # OCR confidence
    # --------------------------

    if len(ocr_results) == 0:

        score -= 40
        reasons.append("No OCR text detected.")

    else:

        avg_conf = sum(
            item["confidence"] for item in ocr_results
        ) / len(ocr_results)

        if avg_conf >= 0.80:
            reasons.append("High OCR confidence.")

        elif avg_conf >= 0.60:
            score -= 10
            reasons.append("Moderate OCR confidence.")

        else:
            score -= 25
            reasons.append("Low OCR confidence.")

    # --------------------------
    # MRZ existence
    # --------------------------

    if not mrz.get("mrz_line_1"):
        score -= 15
        reasons.append("Missing MRZ line 1.")

    if not mrz.get("mrz_line_2"):
        score -= 15
        reasons.append("Missing MRZ line 2.")

    # --------------------------
    # ICAO validation
    # --------------------------

    if validation["passport_checksum"]:
        reasons.append("Passport checksum valid.")
    else:
        score -= 10
        reasons.append("Passport checksum failed.")

    if validation["birth_checksum"]:
        reasons.append("Birth date checksum valid.")
    else:
        score -= 10
        reasons.append("Birth checksum failed.")

    if validation["expiry_checksum"]:
        reasons.append("Expiry checksum valid.")
    else:
        score -= 10
        reasons.append("Expiry checksum failed.")

    if validation["overall_checksum"]:
        reasons.append("Overall ICAO checksum valid.")
    else:
        score -= 15
        reasons.append("Overall checksum failed.")

    # --------------------------
    # AI agreement
    # --------------------------

    similarity = validation["ocr_ai_similarity"]

    if similarity >= 95:

        reasons.append("AI strongly agrees with OCR.")

    elif similarity >= 80:

        score -= 5
        reasons.append("Minor OCR/AI differences.")

    elif similarity >= 60:

        score -= 15
        reasons.append("OCR and AI partially disagree.")

    else:

        score -= 30
        reasons.append("OCR and AI disagree.")

    # --------------------------
    # Clamp score
    # --------------------------

    score = max(0, min(100, score))

    # --------------------------
    # Status
    # --------------------------

    if score >= 90:

        status = "Verified"

    elif score >= 70:

        status = "Review"

    else:

        status = "Rejected"

    return {
        "trust_score": score,
        "status": status,
        "reasons": reasons,
    }