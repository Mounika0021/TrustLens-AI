"""
TrustLens AI
MRZ Extraction Module
"""

import re


def clean_mrz(text: str) -> str:
    """
    Clean OCR output.
    """

    text = text.upper()
    text = text.replace(" ", "")
    text = re.sub(r"[^A-Z0-9<]", "", text)

    return text


def extract_mrz(ocr_results):
    """
    Extract MRZ lines from OCR results.
    """

    lines = []

    for item in ocr_results:
        text = item["text"]

        cleaned = clean_mrz(text)

        if len(cleaned) > 20:
            lines.append(cleaned)

    lines = sorted(lines, key=len, reverse=True)

    mrz1 = lines[0] if len(lines) > 0 else ""
    mrz2 = lines[1] if len(lines) > 1 else ""

    return {
        "mrz_line_1": mrz1,
        "mrz_line_2": mrz2,
    }