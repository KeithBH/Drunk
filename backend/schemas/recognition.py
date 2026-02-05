from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RecognitionResult(BaseModel):
    brand: str | None = None
    category: str | None = None
    abv: float | None = Field(default=None, ge=0, le=100)
    volume_ml: int | None = Field(default=None, gt=0)
    container_count: int | None = Field(default=None, gt=0)
    confidence: float = Field(default=0.0, ge=0, le=1)
    raw_text: str = ""
    needs_review: bool = False


class RecognizeResponse(BaseModel):
    result: RecognitionResult
    corrected_fields: list[str] = Field(default_factory=list)


class DrinkCreateRequest(BaseModel):
    brand: str | None = None
    category: str | None = None
    abv: float | None = Field(default=None, ge=0, le=100)
    volume_ml: int | None = Field(default=None, gt=0)
    container_count: int = Field(default=1, gt=0)
    confidence: float = Field(default=0.0, ge=0, le=1)
    raw_text: str = ""
    needs_review: bool = False


class DrinkRecord(DrinkCreateRequest):
    id: int


def apply_corrections(result: RecognitionResult, corrections: dict[str, Any] | None) -> tuple[RecognitionResult, list[str]]:
    if not corrections:
        return result, []

    corrected_fields: list[str] = []
    allowed_fields = set(result.model_fields.keys()) - {"needs_review"}

    for field, value in corrections.items():
        if field in allowed_fields:
            setattr(result, field, value)
            corrected_fields.append(field)

    return result, corrected_fields
