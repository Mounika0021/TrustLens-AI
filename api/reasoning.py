"""
TrustLens AI
Reasoning Module

Runs the AI model and extracts structured JSON output.
"""

import json
import re

from api.inference import predict


def parse_ai_response(response: str):
    """
    Parse AI response into a dictionary.
    """

    response = response.strip()

    try:
        data = json.loads(response)

        return {
            "mrz_line_1": data.get("mrz_line_1", ""),
            "mrz_line_2": data.get("mrz_line_2", "")
        }

    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")

        return {
            "mrz_line_1": "",
            "mrz_line_2": ""
        }


def reason_about_document(image_path: str):
    """
    Perform AI reasoning on an identity document.

    Args:
        image_path (str): Path to the document image.

    Returns:
        dict: Parsed MRZ extracted by the AI model.
    """

    raw_response = predict(image_path)

    parsed_response = parse_ai_response(raw_response)

    return parsed_response


if __name__ == "__main__":

    image_path = "/content/drive/MyDrive/TrustLens-AI/datasets/MRZ/images/0.png"

    result = reason_about_document(image_path)

    print(result)