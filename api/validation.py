"""
TrustLens AI
ICAO MRZ Validation
"""

from difflib import SequenceMatcher


# ICAO character values
CHAR_VALUES = {
    **{str(i): i for i in range(10)},
    **{chr(ord("A") + i): 10 + i for i in range(26)},
    "<": 0,
}

WEIGHTS = [7, 3, 1]


def char_value(ch):
    return CHAR_VALUES.get(ch, 0)


def calculate_checksum(field: str) -> str:
    """
    Calculate ICAO checksum digit.
    """

    total = 0

    for i, ch in enumerate(field):
        total += char_value(ch) * WEIGHTS[i % 3]

    return str(total % 10)


def validate_field(field: str, check_digit: str) -> bool:
    """
    Validate one MRZ field.
    """

    return calculate_checksum(field) == check_digit


def similarity(a: str, b: str) -> float:
    """
    Percentage similarity between OCR and AI MRZ.
    """

    if not a and not b:
        return 100.0

    return round(
        SequenceMatcher(None, a, b).ratio() * 100,
        2
    )


def validate_mrz(mrz, ai_result):
    """
    Validate ICAO checksums and AI agreement.
    """

    line2 = mrz.get("mrz_line_2", "")

    result = {
        "passport_checksum": False,
        "birth_checksum": False,
        "expiry_checksum": False,
        "overall_checksum": False,
        "ocr_ai_similarity": 0.0,
    }

    if len(line2) >= 44:

        passport = line2[0:9]
        passport_cd = line2[9]

        birth = line2[13:19]
        birth_cd = line2[19]

        expiry = line2[21:27]
        expiry_cd = line2[27]

        personal = line2[28:42]
        personal_cd = line2[42]

        composite = (
            passport
            + passport_cd
            + birth
            + birth_cd
            + expiry
            + expiry_cd
            + personal
        )

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

        result["overall_checksum"] = validate_field(
            composite,
            personal_cd
        )

    ai_line2 = ai_result.get("mrz_line_2", "")

    result["ocr_ai_similarity"] = similarity(
        line2,
        ai_line2,
    )

    return result