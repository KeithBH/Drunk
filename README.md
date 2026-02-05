# Drunk

A lightweight backend service for recording alcohol consumption and generating analytics.

## Data Model

Core tables (SQLite):

- `users`
- `drink_types`
- `drink_records`
- `shares`

`drink_records` includes required fields:

- `user_id`
- `drink_type`
- `abv`
- `volume_ml`
- `count`
- `drank_at`
- `source_image`
- `recognized_payload`

Indexes for aggregation performance:

- `(user_id, drank_at)`
- `(user_id, drink_type)`

## API

### `GET /api/stats/consumption?range=week|month|year&user_id=1`

Returns:

- Total consumption (ml, standard drinks, grams of alcohol)
- Daily trend in the selected range

### `GET /api/stats/favorites?user_id=1&top_n=5`

Returns top N most consumed drink type + brand combinations.

## Unit conversion

A centralized service layer computes:

- Volume in ml
- Standard drinks
- Pure alcohol grams

## Run

```bash
python3 app.py
```

## Test

```bash
python3 -m unittest -v
```
