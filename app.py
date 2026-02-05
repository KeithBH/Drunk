from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

DB_PATH = Path(__file__).with_name("drunk.db")


class Database:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._ensure_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    display_name TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS drink_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    brand TEXT,
                    default_abv REAL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE(name, brand)
                );

                CREATE TABLE IF NOT EXISTS drink_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    drink_type INTEGER NOT NULL,
                    abv REAL NOT NULL,
                    volume_ml REAL NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1,
                    drank_at TEXT NOT NULL,
                    source_image TEXT,
                    recognized_payload TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(drink_type) REFERENCES drink_types(id)
                );

                CREATE TABLE IF NOT EXISTS shares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    drink_record_id INTEGER NOT NULL,
                    share_token TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    expires_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(drink_record_id) REFERENCES drink_records(id)
                );

                CREATE INDEX IF NOT EXISTS idx_drink_records_user_drank_at
                    ON drink_records(user_id, drank_at);

                CREATE INDEX IF NOT EXISTS idx_drink_records_user_drink_type
                    ON drink_records(user_id, drink_type);
                """
            )
            conn.commit()


@dataclass
class UnitMetrics:
    total_volume_ml: float
    total_standard_drinks: float
    total_alcohol_grams: float


class UnitConversionService:
    STANDARD_DRINK_ML = 14.0 / 0.789  # 14g ethanol in ml
    ETHANOL_DENSITY_G_PER_ML = 0.789

    @classmethod
    def volume_to_standard_drinks(cls, volume_ml: float, abv: float) -> float:
        ethanol_ml = volume_ml * abv
        return ethanol_ml / cls.STANDARD_DRINK_ML

    @classmethod
    def volume_to_alcohol_grams(cls, volume_ml: float, abv: float) -> float:
        ethanol_ml = volume_ml * abv
        return ethanol_ml * cls.ETHANOL_DENSITY_G_PER_ML

    @classmethod
    def aggregate_metrics(cls, records: list[sqlite3.Row]) -> UnitMetrics:
        total_volume = 0.0
        total_standard = 0.0
        total_grams = 0.0
        for row in records:
            volume = float(row["volume_ml"]) * int(row["count"])
            abv = float(row["abv"])
            total_volume += volume
            total_standard += cls.volume_to_standard_drinks(volume, abv)
            total_grams += cls.volume_to_alcohol_grams(volume, abv)
        return UnitMetrics(
            total_volume_ml=round(total_volume, 2),
            total_standard_drinks=round(total_standard, 2),
            total_alcohol_grams=round(total_grams, 2),
        )


class StatsService:
    def __init__(self, db: Database, converter: UnitConversionService | None = None):
        self.db = db
        self.converter = converter or UnitConversionService()

    @staticmethod
    def _range_start(now: datetime, range_name: str) -> datetime:
        if range_name == "week":
            return now - timedelta(days=6)
        if range_name == "month":
            return now - timedelta(days=29)
        if range_name == "year":
            return now - timedelta(days=364)
        raise ValueError("range must be one of: week, month, year")

    def consumption(self, user_id: int, range_name: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        start = self._range_start(now, range_name)

        with self.db.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, user_id, drink_type, abv, volume_ml, count, drank_at
                FROM drink_records
                WHERE user_id = ?
                  AND drank_at >= ?
                  AND drank_at <= ?
                ORDER BY drank_at ASC
                """,
                (user_id, start.isoformat(), now.isoformat()),
            ).fetchall()

        totals = self.converter.aggregate_metrics(rows)
        by_day: dict[str, dict[str, float]] = {}
        for row in rows:
            day = row["drank_at"][:10]
            current = by_day.setdefault(
                day,
                {"volume_ml": 0.0, "standard_drinks": 0.0, "alcohol_grams": 0.0},
            )
            volume = float(row["volume_ml"]) * int(row["count"])
            abv = float(row["abv"])
            current["volume_ml"] += volume
            current["standard_drinks"] += self.converter.volume_to_standard_drinks(volume, abv)
            current["alcohol_grams"] += self.converter.volume_to_alcohol_grams(volume, abv)

        trend = [
            {
                "date": day,
                "volume_ml": round(values["volume_ml"], 2),
                "standard_drinks": round(values["standard_drinks"], 2),
                "alcohol_grams": round(values["alcohol_grams"], 2),
            }
            for day, values in sorted(by_day.items())
        ]

        return {
            "range": range_name,
            "start": start.date().isoformat(),
            "end": now.date().isoformat(),
            "totals": {
                "volume_ml": totals.total_volume_ml,
                "standard_drinks": totals.total_standard_drinks,
                "alcohol_grams": totals.total_alcohol_grams,
            },
            "trend": trend,
        }

    def favorites(self, user_id: int, top_n: int = 5) -> dict[str, Any]:
        with self.db.connect() as conn:
            rows = conn.execute(
                """
                SELECT dt.name AS drink_name,
                       COALESCE(dt.brand, 'Unknown') AS brand,
                       COUNT(*) AS records_count,
                       SUM(dr.count) AS drink_count,
                       SUM(dr.volume_ml * dr.count) AS total_volume_ml
                FROM drink_records dr
                JOIN drink_types dt ON dt.id = dr.drink_type
                WHERE dr.user_id = ?
                GROUP BY dr.drink_type, dt.name, dt.brand
                ORDER BY drink_count DESC, total_volume_ml DESC
                LIMIT ?
                """,
                (user_id, top_n),
            ).fetchall()

        favorites = [
            {
                "drink_type": row["drink_name"],
                "brand": row["brand"],
                "records_count": int(row["records_count"]),
                "drink_count": int(row["drink_count"] or 0),
                "total_volume_ml": round(float(row["total_volume_ml"] or 0.0), 2),
            }
            for row in rows
        ]
        return {"top_n": top_n, "favorites": favorites}


class APIHandler(BaseHTTPRequestHandler):
    db = Database()
    stats_service = StatsService(db)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        user_id = int(query.get("user_id", ["1"])[0])

        try:
            if parsed.path == "/api/stats/consumption":
                range_name = query.get("range", ["week"])[0]
                payload = self.stats_service.consumption(user_id=user_id, range_name=range_name)
                self._send_json(payload)
                return

            if parsed.path == "/api/stats/favorites":
                top_n = int(query.get("top_n", ["5"])[0])
                payload = self.stats_service.favorites(user_id=user_id, top_n=top_n)
                self._send_json(payload)
                return

            self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), APIHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
