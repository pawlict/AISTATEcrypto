# Runbook (15 minut): uruchomienie backendu i test Etapu 3

Ten runbook prowadzi krok po kroku od zera do działającego API:
- health
- workspace + role
- watchlista
- flow z kontrolą dostępu workspace

## 0) Wymagania
- Python **3.11+**
- `pip`
- dostęp do internetu (instalacja zależności)

## 1) Setup środowiska
W katalogu repo:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ./backend
```

> Jeśli nie masz `python3.11`, sprawdź `python3 --version` i użyj wersji >= 3.11.

## 2) Start API

```bash
uvicorn app.main:app --reload --app-dir backend
```

Po starcie sprawdź health:

```bash
curl http://127.0.0.1:8000/health
```

Oczekiwane:

```json
{"status":"ok"}
```

## 3) Utwórz user context (`X-User-Email`)

```bash
curl -H "X-User-Email: owner@example.com" http://127.0.0.1:8000/me
```

## 4) Utwórz workspace

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-User-Email: owner@example.com" \
  -d '{"name":"Research BTC"}' \
  http://127.0.0.1:8000/workspaces
```

Zapamiętaj `id` workspace (w przykładach poniżej: `1`).

## 5) Dodaj użytkownika z rolą analyst

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-User-Email: owner@example.com" \
  -d '{"email":"analyst@example.com","role":"analyst"}' \
  http://127.0.0.1:8000/workspaces/1/members
```

Sprawdź listę członków:

```bash
curl -H "X-User-Email: owner@example.com" \
  http://127.0.0.1:8000/workspaces/1/members
```

## 6) Dodaj watchlistę
Jako owner:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-User-Email: owner@example.com" \
  -d '{"chain":"btc","entity_type":"address","entity_value":"bc1qexample...","label":"suspicious"}' \
  http://127.0.0.1:8000/workspaces/1/watchlist
```

Jako analyst (też dozwolone):

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-User-Email: analyst@example.com" \
  -d '{"chain":"btc","entity_type":"address","entity_value":"bc1qexample2...","label":"monitor"}' \
  http://127.0.0.1:8000/workspaces/1/watchlist
```

Pobierz watchlistę:

```bash
curl -H "X-User-Email: owner@example.com" \
  "http://127.0.0.1:8000/workspaces/1/watchlist?chain=btc"
```

## 7) Zasil dane BTC (ingest)
W nowym terminalu (z aktywnym `.venv`):

```bash
python backend/scripts/sync_btc.py --blocks 3
```

## 8) Test endpointu flow (z `workspace_id`)

```bash
curl -H "X-User-Email: owner@example.com" \
  "http://127.0.0.1:8000/flow/btc/bc1qexample...?workspace_id=1&max_edges=200"
```

Oczekiwane:
- 200 OK,
- odpowiedź z `nodes[]`, `edges[]`, `meta`.

## 9) Szybki test kontroli dostępu
Spróbuj użytkownikiem spoza workspace:

```bash
curl -H "X-User-Email: outsider@example.com" \
  "http://127.0.0.1:8000/flow/btc/bc1qexample...?workspace_id=1"
```

Oczekiwane:
- 403 (brak członkostwa w workspace).

## 10) Najczęstsze problemy

### `ModuleNotFoundError: sqlalchemy`
Nieaktywne venv lub brak instalacji:

```bash
source .venv/bin/activate
pip install -e ./backend
```

### Błąd połączenia z API BTC
To problem sieci/providera. Możesz:
- zmniejszyć `--blocks`,
- powtórzyć ingest,
- lub ustawić alternatywny endpoint przez env (patrz `BLOCKSTREAM_API_URL`).

### Python < 3.11
Zainstaluj 3.11 i załóż nowe venv.

## 11) Co dalej po runbooku
- Dodać JWT (zamiast `X-User-Email`) i refresh token.
- Dodać migracje Alembic.
- Podłączyć frontend do endpointów workspace/watchlist/flow.
