from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4


class ShareTarget(str, Enum):
    SELF = "self"
    FRIENDS = "friends"
    PUBLIC = "public"


class ContentScope(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ViewerType(str, Enum):
    ANONYMOUS = "anonymous"
    FRIEND = "friend"
    OWNER = "owner"


@dataclass
class PrivacySettings:
    allow_friend_view: bool = True
    hide_brand_time: bool = True


@dataclass
class DrinkRecord:
    amount_ml: int
    abv_percent: float
    category: str
    brand: str
    happened_at: datetime
    image_url: str | None = None
    note: str | None = None


@dataclass
class ShareData:
    token: str
    owner_id: str
    share_target: ShareTarget
    content_scope: ContentScope
    expires_at: datetime
    privacy: PrivacySettings = field(default_factory=PrivacySettings)
    records: list[DrinkRecord] = field(default_factory=list)
    revoked: bool = False


class ShareStore:
    def __init__(self) -> None:
        self.shares: dict[str, ShareData] = {}

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_record(raw: dict[str, Any]) -> DrinkRecord:
        return DrinkRecord(
            amount_ml=int(raw["amount_ml"]),
            abv_percent=float(raw["abv_percent"]),
            category=str(raw["category"]),
            brand=str(raw["brand"]),
            happened_at=datetime.fromisoformat(raw["happened_at"]),
            image_url=raw.get("image_url"),
            note=raw.get("note"),
        )

    def create_share(self, payload: dict[str, Any]) -> dict[str, Any]:
        token = uuid4().hex
        expires_in_hours = int(payload.get("expires_in_hours", 24))
        expires_at = self._utcnow() + timedelta(hours=expires_in_hours)

        privacy_raw = payload.get("privacy", {})
        privacy = PrivacySettings(
            allow_friend_view=bool(privacy_raw.get("allow_friend_view", True)),
            hide_brand_time=bool(privacy_raw.get("hide_brand_time", True)),
        )

        share = ShareData(
            token=token,
            owner_id=str(payload["owner_id"]),
            share_target=ShareTarget(payload["share_target"]),
            content_scope=ContentScope(payload["content_scope"]),
            expires_at=expires_at,
            privacy=privacy,
            records=[self._parse_record(r) for r in payload.get("records", [])],
        )
        self.shares[token] = share
        return {"token": token, "expires_at": expires_at.isoformat(), "revoked": False}

    def revoke_share(self, token: str, owner_id: str) -> dict[str, bool]:
        share = self.shares.get(token)
        if not share:
            raise KeyError("Share not found")
        if share.owner_id != owner_id:
            raise PermissionError("Only owner can revoke")
        share.revoked = True
        return {"revoked": True}

    def access_share(self, token: str, viewer_type: ViewerType = ViewerType.ANONYMOUS) -> dict[str, Any]:
        share = self.shares.get(token)
        if not share:
            raise KeyError("Share not found")
        if share.revoked:
            raise RuntimeError("Share link has been revoked")
        if share.expires_at <= self._utcnow():
            raise TimeoutError("Share link has expired")
        if viewer_type == ViewerType.FRIEND and not share.privacy.allow_friend_view:
            raise PermissionError("Friend access is disabled")

        summary = self._build_summary(share.records, share.privacy.hide_brand_time)
        return {
            "token": share.token,
            "share_target": share.share_target.value,
            "content_scope": share.content_scope.value,
            "expires_at": share.expires_at.isoformat(),
            "privacy": asdict(share.privacy),
            "summary": summary,
        }

    @staticmethod
    def _build_summary(records: list[DrinkRecord], hide_brand_time: bool) -> dict[str, Any]:
        total_count = len(records)
        total_volume_ml = sum(r.amount_ml for r in records)
        alcohol_ml = round(sum(r.amount_ml * r.abv_percent / 100 for r in records), 2)
        category_counter = Counter(r.category for r in records)

        summary: dict[str, Any] = {
            "total_count": total_count,
            "total_volume_ml": total_volume_ml,
            "estimated_alcohol_ml": alcohol_ml,
            "categories": dict(category_counter),
        }
        if not hide_brand_time:
            summary["brands"] = dict(Counter(r.brand for r in records))
            summary["hours"] = dict(sorted(Counter(r.happened_at.hour for r in records).items()))
        return summary


share_store = ShareStore()


class ShareHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _parse_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body.decode("utf-8"))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/share":
            try:
                result = share_store.create_share(self._parse_body())
                return self._send_json(result)
            except Exception as exc:  # noqa: BLE001
                return self._send_json({"detail": str(exc)}, HTTPStatus.BAD_REQUEST)

        if parsed.path.startswith("/api/share/") and parsed.path.endswith("/revoke"):
            token = parsed.path.split("/")[3]
            params = parse_qs(parsed.query)
            owner_id = params.get("owner_id", [""])[0]
            try:
                result = share_store.revoke_share(token, owner_id)
                return self._send_json(result)
            except KeyError as exc:
                return self._send_json({"detail": str(exc)}, HTTPStatus.NOT_FOUND)
            except PermissionError as exc:
                return self._send_json({"detail": str(exc)}, HTTPStatus.FORBIDDEN)

        self._send_json({"detail": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/share/"):
            token = parsed.path.split("/")[3]
            params = parse_qs(parsed.query)
            viewer = ViewerType(params.get("viewer_type", [ViewerType.ANONYMOUS.value])[0])
            try:
                result = share_store.access_share(token, viewer)
                return self._send_json(result)
            except KeyError as exc:
                return self._send_json({"detail": str(exc)}, HTTPStatus.NOT_FOUND)
            except PermissionError as exc:
                return self._send_json({"detail": str(exc)}, HTTPStatus.FORBIDDEN)
            except (RuntimeError, TimeoutError) as exc:
                return self._send_json({"detail": str(exc)}, HTTPStatus.GONE)

        self._send_json({"detail": "Not found"}, HTTPStatus.NOT_FOUND)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ShareHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
