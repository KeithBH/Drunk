from __future__ import annotations

import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from backend.schemas.recognition import (
    DrinkCreateRequest,
    DrinkRecord,
    RecognizeResponse,
    apply_corrections,
)
from backend.services.alcohol_recognition import AlcoholRecognitionService

app = FastAPI(title="Drunk API")

recognition_service = AlcoholRecognitionService()
_drinks_db: list[DrinkRecord] = []


@app.post("/api/recognize", response_model=RecognizeResponse)
async def recognize_image(
    image: UploadFile = File(...),
    corrections: str | None = Form(default=None),
) -> RecognizeResponse:
    image_bytes = await image.read()
    recognized = recognition_service.recognize(image_bytes=image_bytes, filename=image.filename)

    parsed_corrections: dict | None = None
    if corrections:
        try:
            parsed_corrections = json.loads(corrections)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid corrections JSON") from exc

    corrected_result, corrected_fields = apply_corrections(recognized, parsed_corrections)
    corrected_result.needs_review = corrected_result.needs_review or corrected_result.confidence < 0.7

    return RecognizeResponse(result=corrected_result, corrected_fields=corrected_fields)


@app.post("/api/drinks", response_model=DrinkRecord, status_code=201)
def create_drink(drink: DrinkCreateRequest) -> DrinkRecord:
    drink_id = len(_drinks_db) + 1
    record = DrinkRecord(id=drink_id, **drink.model_dump())
    _drinks_db.append(record)
    return record


@app.get("/api/drinks", response_model=list[DrinkRecord])
def list_drinks() -> list[DrinkRecord]:
    return _drinks_db
