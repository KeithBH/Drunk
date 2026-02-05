import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta, timezone

from app.main import ShareStore, ViewerType


def _sample_payload(hide_brand_time=True, allow_friend_view=True, expires_in_hours=2):
    return {
        "owner_id": "u-1",
        "share_target": "friends",
        "content_scope": "weekly",
        "expires_in_hours": expires_in_hours,
        "privacy": {
            "allow_friend_view": allow_friend_view,
            "hide_brand_time": hide_brand_time,
        },
        "records": [
            {
                "amount_ml": 500,
                "abv_percent": 5,
                "category": "beer",
                "brand": "A",
                "happened_at": datetime(2026, 1, 1, 20, tzinfo=timezone.utc).isoformat(),
                "image_url": "https://example.com/1.png",
                "note": "sensitive",
            },
            {
                "amount_ml": 30,
                "abv_percent": 40,
                "category": "spirit",
                "brand": "B",
                "happened_at": datetime(2026, 1, 1, 21, tzinfo=timezone.utc).isoformat(),
                "image_url": "https://example.com/2.png",
                "note": "sensitive2",
            },
        ],
    }


def test_share_default_only_returns_aggregate():
    store = ShareStore()
    created = store.create_share(_sample_payload())

    payload = store.access_share(created["token"])
    assert payload["summary"]["total_count"] == 2
    assert "brands" not in payload["summary"]
    assert "hours" not in payload["summary"]


def test_share_can_include_brand_and_time_aggregate():
    store = ShareStore()
    created = store.create_share(_sample_payload(hide_brand_time=False))

    payload = store.access_share(created["token"])
    assert payload["summary"]["brands"] == {"A": 1, "B": 1}
    assert payload["summary"]["hours"] == {20: 1, 21: 1}


def test_friend_access_respects_privacy_setting():
    store = ShareStore()
    created = store.create_share(_sample_payload(allow_friend_view=False))

    try:
        store.access_share(created["token"], ViewerType.FRIEND)
    except PermissionError:
        pass
    else:
        raise AssertionError("Expected friend access to be blocked")


def test_share_supports_manual_revoke_and_expiry():
    store = ShareStore()
    created = store.create_share(_sample_payload())
    token = created["token"]

    revoke = store.revoke_share(token, "u-1")
    assert revoke["revoked"] is True

    try:
        store.access_share(token)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected revoked share to be inaccessible")

    created2 = store.create_share(_sample_payload())
    share = store.shares[created2["token"]]
    share.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    try:
        store.access_share(created2["token"])
    except TimeoutError:
        pass
    else:
        raise AssertionError("Expected expired share to be inaccessible")
