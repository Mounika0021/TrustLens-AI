
"""
TrustLens AI
Reasoning Module

Runs the fine-tuned Qwen2-VL model
and converts its output into the
standard TrustLens AI schema.
"""

import json
import re

from api.inference import predict


def parse_ai_response(response: str):
    """
    Convert different model JSON formats into
    the standard TrustLens-AI result format.
    """

    # --------------------------------------------------
    # Empty response
    # --------------------------------------------------

    if not response:

        return {
            "document_type": "Unknown",
            "verification_status": "Rejected",
            "confidence": 0.0,
            "mrz_line_1": "",
            "mrz_line_2": "",
        }


    response = response.strip()


    # --------------------------------------------------
    # Remove markdown JSON fences
    # --------------------------------------------------

    response = re.sub(
        r"```json\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"```\s*$",
        "",
        response
    )

    response = response.strip()


    # --------------------------------------------------
    # Parse JSON
    # --------------------------------------------------

    try:

        data = json.loads(response)

    except json.JSONDecodeError as e:

        print(
            "JSON parsing failed:",
            e
        )

        return {
            "document_type": "Unknown",
            "verification_status": "Rejected",
            "confidence": 0.0,
            "mrz_line_1": "",
            "mrz_line_2": "",
        }


    # ==================================================
    # DOCUMENT TYPE
    # ==================================================

    document_type = data.get(
        "document_type"
    )

    # Fine-tuned model may return:
    #
    # system_id = Aadhaar / PAN / Passport

    if not document_type:

        document_type = data.get(
            "system_id"
        )

    if not document_type:

        document_type = "Unknown"


    # ==================================================
    # VERIFICATION STATUS
    # ==================================================

    raw_status = data.get(
        "verification_status"
    )

    system_type = data.get(
        "system_type"
    )


    # Normalize status

    if raw_status:

        status_text = str(
            raw_status
        ).strip().lower()

    else:

        status_text = ""


    if status_text in [
        "pass",
        "passed",
        "verified",
        "verify",
        "valid"
    ]:

        verification_status = "Verified"

    elif status_text in [
        "fail",
        "failed",
        "rejected",
        "invalid"
    ]:

        verification_status = "Rejected"

    elif system_type:

        system_type_text = str(
            system_type
        ).strip().lower()

        if system_type_text in [
            "pass",
            "passed",
            "verified",
            "valid"
        ]:

            verification_status = "Verified"

        elif system_type_text in [
            "fail",
            "failed",
            "rejected",
            "invalid"
        ]:

            verification_status = "Rejected"

        else:

            verification_status = (
                "Verified"
                if document_type != "Unknown"
                else "Rejected"
            )

    else:

        verification_status = (
            "Verified"
            if document_type != "Unknown"
            else "Rejected"
        )


    # ==================================================
    # CONFIDENCE
    # ==================================================

    confidence_value = data.get(
        "confidence"
    )


    if confidence_value is not None:

        try:

            confidence = float(
                confidence_value
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0

    else:

        # --------------------------------------------------
        # The model sometimes omits confidence.
        #
        # If it explicitly classified the document as
        # Verified/Pass, use 1.0 rather than incorrectly
        # treating the missing field as model failure.
        # --------------------------------------------------

        if verification_status == "Verified":

            confidence = 1.0

        else:

            confidence = 0.0


    # Clamp confidence

    confidence = max(
        0.0,
        min(
            1.0,
            confidence
        )
    )


    # ==================================================
    # MRZ
    # ==================================================

    mrz_line_1 = data.get(
        "mrz_line_1",
        ""
    ) or ""


    mrz_line_2 = data.get(
        "mrz_line_2",
        ""
    ) or ""


    # ==================================================
    # FINAL STANDARD RESULT
    # ==================================================

    return {

        "document_type": document_type,

        "verification_status":
            verification_status,

        "confidence":
            confidence,

        "mrz_line_1":
            mrz_line_1,

        "mrz_line_2":
            mrz_line_2,
    }


def reason_about_document(image_path: str):
    """
    Run the fine-tuned Qwen2-VL model
    and return a normalized result.
    """

    raw_response = predict(
        image_path
    )

    return parse_ai_response(
        raw_response
    )


if __name__ == "__main__":

    image_path = (
        "/content/drive/MyDrive/TrustLens-AI/"
        "datasets/MRZ/images/0.png"
    )

    result = reason_about_document(
        image_path
    )

    print(result)
