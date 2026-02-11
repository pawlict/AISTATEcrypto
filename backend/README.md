# Backend (Stage 1)

Minimalna implementacja etapu 1 (BTC ingest + model danych):

- FastAPI app z endpointem health
- SQLAlchemy modele `chain_transaction`, `transfer_edge`, `tracked_entity`
- Serwis ingest BTC pobierający ostatnie bloki i transakcje z Blockstream API
- CLI do synchronizacji ostatnich N bloków

## Szybki start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./backend
python backend/scripts/sync_btc.py --blocks 3
uvicorn app.main:app --reload
```

> Domyślna baza: SQLite (`backend/data/app.db`) dla łatwego startu. W produkcji ustaw `DATABASE_URL` na PostgreSQL.
