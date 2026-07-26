"""
TrustLens AI
Response Schemas
"""

from typing import List
from pydantic import BaseModel


class OCRResult(BaseModel):
    box: List[List[int]]
    text: str
    confidence: float


class AIResult(BaseModel):
    mrz_line_1: str
    mrz_line_2: str


class ValidationResult(BaseModel):
    passport_checksum: bool
    birth_checksum: bool
    expiry_checksum: bool
    overall_checksum: bool
    ocr_ai_similarity: float


class TrustResponse(BaseModel):
    trust_score: int
    status: str
    reasons: List[str]


class VerifyResponse(BaseModel):
    ocr: List[OCRResult]
    mrz: dict
    ai_result: AIResult
    validation: ValidationResult
    trust: TrustResponse