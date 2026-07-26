"""
TrustLens AI
FastAPI Backend
"""

import os
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


app = FastAPI(
    title="TrustLens AI",
    version="2.0",
    description="AI-powered Identity Document Verification"
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "Welcome to TrustLens AI 🚀"
    }


@app.post(
    "/verify",
    response_model=VerifyResponse
)
async def verify_document(
    file: UploadFile = File(...)
):

    try:

        image_path = UPLOAD_DIR / file.filename

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ocr_results = extract_text(str(image_path))

        mrz = extract_mrz(ocr_results)

        ai_result = reason_about_document(
            str(image_path)
        )

        validation = validate_mrz(
            mrz,
            ai_result
        )


        trust = calculate_trust_score(
            ocr_results,
            mrz,
            ai_result,
            validation
        )

        return VerifyResponse(
            ocr=ocr_results,
            mrz=mrz,
            ai_result=ai_result,
            validation=validation,
            trust=trust
        )

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )

    finally:

        if image_path.exists():
            os.remove(image_path)