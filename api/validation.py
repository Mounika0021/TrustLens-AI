
"""
TrustLens AI
Document-Aware Validation

Passport:
    ICAO MRZ checksum validation

Aadhaar:
    12-digit Aadhaar format validation

PAN:
    10-character PAN format validation
"""

import re
from difflib import SequenceMatcher


# ============================================================
# ICAO MRZ CHARACTER VALUES
# ============================================================

CHAR_VALUES = {
    **{
        str(i): i
        for i in range(10)
    },

    **{
        chr(ord("A") + i): 10 + i
        for i in range(26)
    },

    "<": 0,
}

WEIGHTS = [7, 3, 1]


# ============================================================
# BASIC HELPERS
# ============================================================

def char_value(ch):
    return CHAR_VALUES.get(ch, 0)


def calculate_checksum(field: str) -> str:

    total = 0

    for i, ch in enumerate(field):

        total += (
            char_value(ch)
            * WEIGHTS[i % 3]
        )

    return str(total % 10)


def validate_field(
    field: str,
    check_digit: str
) -> bool:

    if not field:
        return False

    if not check_digit:
        return False

    return (
        calculate_checksum(field)
        == check_digit
    )


def similarity(
    a: str,
    b: str
) -> float:

    if not a or not b:
        return 0.0

    return round(
        SequenceMatcher(
            None,
            a,
            b
        ).ratio() * 100,
        2
    )


def get_ocr_text(
    ocr_results
) -> str:
    """
    Combine all OCR text into one normalized string.
    """

    if not ocr_results:
        return ""

    texts = []

    for item in ocr_results:

        if isinstance(item, dict):

            text = item.get(
                "text",
                ""
            )

        else:

            text = getattr(
                item,
                "text",
                ""
            )

        if text:
            texts.append(
                str(text)
            )

    return " ".join(texts)


# ============================================================
# PASSPORT VALIDATION
# ============================================================

def validate_passport(
    mrz,
    ai_result
):

    line2 = str(
        mrz.get(
            "mrz_line_2",
            ""
        )
        or ""
    ).upper()

    # Remove spaces introduced by OCR
    line2 = line2.replace(
        " ",
        ""
    )

    result = {
        "passport_checksum": False,
        "birth_checksum": False,
        "expiry_checksum": False,
        "overall_checksum": False,
        "ocr_ai_similarity": 0.0,
        "format_valid": False,
        "checks": [],
    }

    # Passport MRZ line 2 must contain 44 characters
    if len(line2) != 44:

        result["checks"].append(
            "Passport MRZ line 2 must contain exactly 44 characters."
        )

        return result

    result["format_valid"] = True

    # --------------------------------------------------------
    # Passport number
    # --------------------------------------------------------

    passport = line2[0:9]
    passport_cd = line2[9]

    # --------------------------------------------------------
    # Date of birth
    # --------------------------------------------------------

    birth = line2[13:19]
    birth_cd = line2[19]

    # --------------------------------------------------------
    # Expiry date
    # --------------------------------------------------------

    expiry = line2[21:27]
    expiry_cd = line2[27]

    # --------------------------------------------------------
    # Personal number
    # --------------------------------------------------------

    personal = line2[28:42]
    personal_cd = line2[42]

    # --------------------------------------------------------
    # Checksums
    # --------------------------------------------------------

    result["passport_checksum"] = validate_field(
        passport,
        passport_cd
    )

    result["birth_checksum"] = validate_field(
        birth,
        birth_cd
    )

    result["expiry_checksum"] = validate_field(
        expiry,
        expiry_cd
    )

    composite = (
        passport
        + passport_cd
        + birth
        + birth_cd
        + expiry
        + expiry_cd
        + personal
    )

    result["overall_checksum"] = validate_field(
        composite,
        personal_cd
    )

    # --------------------------------------------------------
    # Check messages
    # --------------------------------------------------------

    if result["passport_checksum"]:

        result["checks"].append(
            "Passport number checksum valid."
        )

    else:

        result["checks"].append(
            "Passport number checksum failed."
        )

    if result["birth_checksum"]:

        result["checks"].append(
            "Birth date checksum valid."
        )

    else:

        result["checks"].append(
            "Birth date checksum failed."
        )

    if result["expiry_checksum"]:

        result["checks"].append(
            "Expiry date checksum valid."
        )

    else:

        result["checks"].append(
            "Expiry date checksum failed."
        )

    if result["overall_checksum"]:

        result["checks"].append(
            "Overall ICAO checksum valid."
        )

    else:

        result["checks"].append(
            "Overall ICAO checksum failed."
        )

    # --------------------------------------------------------
    # OCR ↔ AI MRZ similarity
    # --------------------------------------------------------

    ai_line2 = str(
        ai_result.get(
            "mrz_line_2",
            ""
        )
        or ""
    ).upper().replace(
        " ",
        ""
    )

    if ai_line2:

        result["ocr_ai_similarity"] = similarity(
            line2,
            ai_line2
        )

        result["checks"].append(
            "OCR/AI MRZ similarity: "
            f"{result['ocr_ai_similarity']:.2f}%."
        )

    else:

        result["checks"].append(
            "AI MRZ comparison not available."
        )

    return result


# ============================================================
# AADHAAR VALIDATION
# ============================================================

def validate_aadhaar(
    ocr_results
):

    text = get_ocr_text(
        ocr_results
    )

    # Keep digits only
    digits = re.sub(
        r"[^0-9]",
        "",
        text
    )

    result = {
        "passport_checksum": False,
        "birth_checksum": False,
        "expiry_checksum": False,
        "overall_checksum": False,
        "ocr_ai_similarity": 0.0,
        "format_valid": False,
        "checks": [],
    }

    # --------------------------------------------------------
    # Detect a 12-digit Aadhaar-like number
    # --------------------------------------------------------

    aadhaar_match = re.search(
        r"\d{12}",
        digits
    )

    if aadhaar_match:

        aadhaar_number = aadhaar_match.group(0)

        result["format_valid"] = True

        # Store only a safe masked representation in logs/checks
        masked = (
            "XXXX XXXX "
            + aadhaar_number[-4:]
        )

        result["checks"].append(
            f"Aadhaar 12-digit format detected: {masked}."
        )

    else:

        result["checks"].append(
            "Aadhaar 12-digit number not confidently detected."
        )

    result["checks"].append(
        "Passport MRZ validation is not applicable to Aadhaar."
    )

    return result


# ============================================================
# PAN VALIDATION
# ============================================================

def validate_pan(
    ocr_results
):

    text = get_ocr_text(
        ocr_results
    ).upper()

    # Remove spaces and punctuation
    normalized = re.sub(
        r"[^A-Z0-9]",
        "",
        text
    )

    result = {
        "passport_checksum": False,
        "birth_checksum": False,
        "expiry_checksum": False,
        "overall_checksum": False,
        "ocr_ai_similarity": 0.0,
        "format_valid": False,
        "checks": [],
    }

    # Standard PAN pattern:
    # 5 letters + 4 digits + 1 letter
    #
    # Example format:
    # ABCDE1234F

    pan_match = re.search(
        r"[A-Z]{5}[0-9]{4}[A-Z]",
        normalized
    )

    if pan_match:

        pan_number = pan_match.group(0)

        result["format_valid"] = True

        masked = (
            "XXXXX"
            + pan_number[5:9]
            + "X"
        )

        result["checks"].append(
            f"PAN format detected: {masked}."
        )

    else:

        result["checks"].append(
            "PAN 10-character format not confidently detected."
        )

    result["checks"].append(
        "Passport MRZ validation is not applicable to PAN."
    )

    return result


# ============================================================
# MAIN DOCUMENT VALIDATOR
# ============================================================

def validate_mrz(
    mrz,
    ai_result,
    ocr_results=None
):
    """
    Route validation according to document type.

    This keeps the existing function name for compatibility
    with api.app.
    """

    document_type = str(
        ai_result.get(
            "document_type",
            "Unknown"
        )
        or "Unknown"
    ).strip().lower()

    # --------------------------------------------------------
    # Passport
    # --------------------------------------------------------

    if document_type == "passport":

        return validate_passport(
            mrz,
            ai_result
        )

    # --------------------------------------------------------
    # Aadhaar
    # --------------------------------------------------------

    if document_type == "aadhaar":

        return validate_aadhaar(
            ocr_results or []
        )

    # --------------------------------------------------------
    # PAN
    # --------------------------------------------------------

    if document_type == "pan":

        return validate_pan(
            ocr_results or []
        )

    # --------------------------------------------------------
    # Unknown / unsupported
    # --------------------------------------------------------

    return {
        "passport_checksum": False,
        "birth_checksum": False,
        "expiry_checksum": False,
        "overall_checksum": False,
        "ocr_ai_similarity": 0.0,
        "format_valid": False,
        "checks": [
            "Document-specific validation unavailable."
        ],
    }
