# Drunk

Record your poison.

## Share API

This repository includes a Python HTTP service with sharing capabilities:

- `POST /api/share`: create a share link with share target, content scope, expiry, token, privacy settings, and source records.
- `GET /api/share/{token}`: fetch a privacy-safe share view (aggregated stats only by default).
- `POST /api/share/{token}/revoke?owner_id=<id>`: manually revoke a share link.

### Privacy defaults

- Share response hides raw records, image links, and notes.
- Brand/time details are hidden by default and can be toggled by `privacy.hide_brand_time`.
- Friend access can be toggled by `privacy.allow_friend_view`.

### Run

```bash
python app/main.py
```

### Test

```bash
pytest -q
```
