
"""
TrustLens AI
Response Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class OCRResult(BaseModel):
    box: List[List[int]] = Field(default_factory=list)
    text: str = ""
    confidence: float = 0.0


class AIResult(BaseModel):
    document_type: str = "Unknown"
    verification_status: str = "Rejected"
    confidence: float = 0.0
    mrz_line_1: Optional[str] = None
    mrz_line_2: Optional[str] = None


class ValidationResult(BaseModel):
    passport_checksum: bool = False
    birth_checksum: bool = False
    expiry_checksum: bool = False
    overall_checksum: bool = False
    ocr_ai_similarity: float = 0.0
    format_valid: Optional[bool] = None
    checks: List[str] = Field(default_factory=list)


class TrustResponse(BaseModel):
    trust_score: int
    status: str
    reasons: List[str] = Field(default_factory=list)


class VerifyResponse(BaseModel):
    ocr: List[OCRResult] = Field(default_factory=list)
    mrz: dict = Field(default_factory=dict)
    ai_result: AIResult
    validation: ValidationResult
    trust: TrustResponse
