
"""
TrustLens AI
FastAPI Backend

Pipeline:

Upload
  -> OCR
  -> MRZ / field extraction
  -> Qwen2-VL reasoning
  -> document-type reconciliation
  -> document-specific validation
  -> trust score
  -> JSON response
"""

import os
import re
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from api.ocr import extract_text
from api.mrz import extract_mrz
from api.reasoning import reason_about_document
from api.validation import validate_mrz
from api.trust_score import calculate_trust_score
from api.schemas import VerifyResponse


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="TrustLens AI",
    version="3.2",
    description=(
        "AI-powered identity document verification using "
        "OCR, Vision-Language AI, document-type reconciliation, "
        "validation and trust scoring."
    )
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path(
    "/content/drive/MyDrive/TrustLens-AI/uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPERS
# ============================================================

def get_ocr_text(ocr_results):
    """
    Combine OCR output into one uppercase string.
    """

    texts = []

    for item in ocr_results or []:

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

    return " ".join(texts).upper()


def normalize_mrz_line(line):
    """
    Normalize OCR/MRZ text for structural checks.
    """

    if not line:
        return ""

    return re.sub(
        r"[^A-Z0-9<]",
        "",
        str(line).upper()
    )


def reconcile_document_type(
    ai_result,
    ocr_results,
    mrz
):
    """
    Reconcile AI classification with strong structural
    evidence from OCR and MRZ.

    The AI result remains the primary classifier, but
    strong passport evidence can override an incorrect
    PAN/Aadhaar/Unknown classification.
    """

    ai_result = dict(
        ai_result or {}
    )

    ai_type = str(
        ai_result.get(
            "document_type",
            "Unknown"
        )
    ).strip()

    ai_type_lower = ai_type.lower()

    ocr_text = get_ocr_text(
        ocr_results
    )

    line1 = normalize_mrz_line(
        mrz.get(
            "mrz_line_1",
            ""
        )
        if mrz else ""
    )

    line2 = normalize_mrz_line(
        mrz.get(
            "mrz_line_2",
            ""
        )
        if mrz else ""
    )

    # ========================================================
    # PASSPORT EVIDENCE
    # ========================================================

    passport_signals = 0

    # Strongest MRZ signal:
    # Passport MRZ line 1 begins with P<
    if line1.startswith("P<"):

        passport_signals += 3

    # Passport MRZ line 2 should be 44 characters
    if len(line2) == 44:

        passport_signals += 3

    # OCR field indicators
    if "PASSPORT NO" in ocr_text:
        passport_signals += 2

    if "PASSPORT" in ocr_text:
        passport_signals += 1

    if "COUNTRY CODE" in ocr_text:
        passport_signals += 1

    if "/TYPE" in ocr_text or "TYPE" in ocr_text:
        passport_signals += 1

    # ========================================================
    # PAN EVIDENCE
    # ========================================================

    pan_matches = re.findall(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        ocr_text
    )

    pan_strong = len(
        pan_matches
    ) > 0

    # ========================================================
    # AADHAAR EVIDENCE
    # ========================================================

    digit_string = re.sub(
        r"[^0-9]",
        "",
        ocr_text
    )

    aadhaar_match = re.search(
        r"\d{12}",
        digit_string
    )

    aadhaar_strong = (
        aadhaar_match is not None
    )

    # ========================================================
    # RECONCILIATION RULE
    # ========================================================

    # Strong passport evidence overrides a conflicting
    # AI classification.

    if passport_signals >= 3:

        ai_result["document_type"] = "Passport"

        # Keep an explanation for debugging.
        ai_result["_classification_source"] = (
            "AI + strong passport OCR/MRZ evidence"
        )

        return ai_result

    # If AI already says PAN and there is a valid PAN pattern,
    # keep PAN.
    if ai_type_lower == "pan" and pan_strong:

        ai_result["_classification_source"] = (
            "AI + PAN format evidence"
        )

        return ai_result

    # If AI says Aadhaar and a strong Aadhaar number exists,
    # keep Aadhaar.
    if ai_type_lower == "aadhaar" and aadhaar_strong:

        ai_result["_classification_source"] = (
            "AI + Aadhaar number evidence"
        )

        return ai_result

    # Otherwise preserve the AI classification.
    ai_result["_classification_source"] = (
        "AI classification"
    )

    return ai_result


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to TrustLens AI 🚀",
        "status": "running",
        "version": app.version,
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "TrustLens AI",
        "version": app.version,
    }


# ============================================================
# VERIFY
# ============================================================

@app.post(
    "/verify",
    response_model=VerifyResponse
)
async def verify_document(
    file: UploadFile = File(...)
):

    image_path = None

    try:

        # ----------------------------------------------------
        # FILE CHECK
        # ----------------------------------------------------

        if not file.filename:

            return JSONResponse(
                status_code=400,
                content={
                    "error": "No filename supplied."
                }
            )

        safe_filename = Path(
            file.filename
        ).name

        image_path = (
            UPLOAD_DIR
            / safe_filename
        )

        # ----------------------------------------------------
        # SAVE FILE
        # ----------------------------------------------------

        with open(
            image_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # ====================================================
        # STEP 1 — OCR
        # ====================================================

        ocr_results = extract_text(
            str(image_path)
        )

        # ====================================================
        # STEP 2 — MRZ / FIELD EXTRACTION
        # ====================================================

        mrz = extract_mrz(
            ocr_results
        )

        # ====================================================
        # STEP 3 — AI REASONING
        # ====================================================

        ai_result = reason_about_document(
            str(image_path)
        )

        # ====================================================
        # STEP 4 — DOCUMENT TYPE RECONCILIATION
        # ====================================================

        ai_result = reconcile_document_type(
            ai_result,
            ocr_results,
            mrz
        )

        # Remove internal debug metadata before response
        ai_result.pop(
            "_classification_source",
            None
        )

        # ====================================================
        # STEP 5 — DOCUMENT-SPECIFIC VALIDATION
        # ====================================================

        validation = validate_mrz(
            mrz,
            ai_result,
            ocr_results
        )

        # ====================================================
        # STEP 6 — TRUST SCORE
        # ====================================================

        trust = calculate_trust_score(
            ocr_results,
            mrz,
            ai_result,
            validation
        )

        # ====================================================
        # STEP 7 — RESPONSE
        # ====================================================

        return VerifyResponse(
            ocr=ocr_results,
            mrz=mrz,
            ai_result=ai_result,
            validation=validation,
            trust=trust
        )

    except Exception as e:

        print(
            "❌ TrustLens API error:",
            repr(e)
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )

    finally:

        if (
            image_path is not None
            and image_path.exists()
        ):

            try:

                os.remove(
                    image_path
                )

            except Exception as cleanup_error:

                print(
                    "⚠️ Cleanup failed:",
                    cleanup_error
                )
