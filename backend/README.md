# Backend (Stage 1 + Stage 2 + Stage 3)

Aktualna implementacja obejmuje:

- FastAPI app z endpointem health
- SQLAlchemy modele `chain_transaction`, `transfer_edge`, `tracked_entity`
- Serwis ingest BTC pobierający ostatnie bloki i transakcje z Blockstream API
- CLI do synchronizacji ostatnich N bloków
- Endpoint grafu przepływów `GET /flow/{chain}/{entity}` z filtrami
- Multiuser podstawy: użytkownicy, workspace, role, watchlista per workspace

## Szybki start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./backend
python backend/scripts/sync_btc.py --blocks 3
uvicorn app.main:app --reload
```

> Domyślna baza: SQLite (`backend/data/app.db`) dla łatwego startu. W produkcji ustaw `DATABASE_URL` na PostgreSQL.

## Uwierzytelnianie (wersja developerska)

Na tym etapie API korzysta z nagłówka `X-User-Email`.

Przykład:

```bash
curl -H "X-User-Email: owner@example.com" http://127.0.0.1:8000/me
```

## Workspace i role

Endpointy:
- `POST /workspaces`
- `GET /workspaces`
- `POST /workspaces/{workspace_id}/members` (tylko owner)
- `GET /workspaces/{workspace_id}/members`
- `POST /workspaces/{workspace_id}/watchlist` (owner/analyst)
- `GET /workspaces/{workspace_id}/watchlist`

Role:
- `owner`
- `analyst`
- `viewer`

## Endpoint flow

`GET /flow/{chain}/{entity}`

Parametry query:
- `workspace_id` (**wymagany**)
- `time_from` (ISO datetime, opcjonalnie)
- `time_to` (ISO datetime, opcjonalnie)
- `min_amount_sats` (opcjonalnie)
- `max_edges` (domyślnie 500, max 2000)

Przykład:

```bash
curl -H "X-User-Email: owner@example.com" \
  "http://127.0.0.1:8000/flow/btc/bc1...?...&workspace_id=1&max_edges=200"
```
