from __future__ import annotations

import re

from backend.schemas.recognition import RecognitionResult

LOW_CONFIDENCE_THRESHOLD = 0.7


class AlcoholRecognitionService:
    """Simple text-based recognizer placeholder.

    In production this can be replaced with OCR + model inference.
    """

    def recognize(self, image_bytes: bytes, filename: str | None = None) -> RecognitionResult:
        raw_text = self._extract_text(image_bytes, filename)

        brand = self._extract_brand(raw_text)
        category = self._extract_category(raw_text)
        abv = self._extract_abv(raw_text)
        volume_ml = self._extract_volume(raw_text)
        container_count = self._extract_count(raw_text)

        identified = sum(value is not None for value in [brand, category, abv, volume_ml, container_count])
        confidence = min(1.0, identified / 5)

        result = RecognitionResult(
            brand=brand,
            category=category,
            abv=abv,
            volume_ml=volume_ml,
            container_count=container_count,
            confidence=confidence,
            raw_text=raw_text,
            needs_review=confidence < LOW_CONFIDENCE_THRESHOLD,
        )
        return result

    @staticmethod
    def _extract_text(image_bytes: bytes, filename: str | None = None) -> str:
        if filename:
            return filename.lower()

        try:
            text = image_bytes.decode("utf-8")
            return text.lower()
        except UnicodeDecodeError:
            return ""

    @staticmethod
    def _extract_brand(text: str) -> str | None:
        known_brands = ["heineken", "budweiser", "corona", "asahi", "tsingtao", "jack daniel's"]
        for brand in known_brands:
            if brand in text:
                return brand
        return None

    @staticmethod
    def _extract_category(text: str) -> str | None:
        category_map = {
            "beer": "beer",
            "lager": "beer",
            "wine": "wine",
            "whisky": "whisky",
            "whiskey": "whisky",
            "vodka": "vodka",
            "rum": "rum",
            "soju": "soju",
            "sake": "sake",
        }
        for token, category in category_map.items():
            if token in text:
                return category
        return None

    @staticmethod
    def _extract_abv(text: str) -> float | None:
        match = re.search(r"(\d{1,2}(?:\.\d)?)\s*%", text)
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def _extract_volume(text: str) -> int | None:
        match = re.search(r"(\d{2,4})\s*ml", text)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _extract_count(text: str) -> int | None:
        pack_match = re.search(r"(\d{1,2})\s*(?:pack|bottles|cans)", text)
        if pack_match:
            return int(pack_match.group(1))

        multiplication_match = re.search(r"x\s*(\d{1,2})", text)
        if multiplication_match:
            return int(multiplication_match.group(1))

        return None
