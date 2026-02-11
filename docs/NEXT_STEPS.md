# Co dalej? Plan wykonawczy (BTC-first -> ETH)

Ten dokument zamienia strategię na konkretne kroki do wykonania sprint po sprincie.

## Założenie
- Cel MVP: wykrywanie i wizualizacja przepływów na BTC, z późniejszym rozszerzeniem o ETH.
- Architektura od początku: multi-chain + multiuser.

## Sprint 0 (1-2 dni): decyzje i repo

### Decyzje techniczne (zamknąć przed kodowaniem)
- Backend: **FastAPI** (Python) lub **NestJS** (TypeScript). 
- Frontend: **Next.js + TypeScript**.
- DB: **PostgreSQL**.
- Kolejka: **Redis + worker**.
- Provider danych BTC (na start):
  - A) publiczny API (szybki start),
  - B) własny node/indexer (większa kontrola).

### Definition of Done sprintu 0
- [ ] Wybrane technologie i zapisane w README.
- [ ] Utworzone issue dla Sprint 1.
- [ ] Przygotowany minimalny model danych (DDL v0).

## Sprint 1 (1 tydzień): BTC ingest + model danych

### Zakres
- Ingest bloków i transakcji BTC.
- Parsowanie `inputs/outputs`, opłat i timestamp.
- Zapis do tabel: `chain_transaction`, `transfer_edge`.

### Minimalne tabele (v0)
- `chain_transaction(id, chain, tx_hash, block_number, block_time, fee_sats, raw_json)`
- `transfer_edge(id, chain, tx_hash, src_entity, dst_entity, amount_sats, asset_symbol, block_time)`
- `tracked_entity(id, workspace_id, chain, entity_type, entity_value, label)`

### Definition of Done sprintu 1
- [ ] Działa synchronizacja ostatnich N bloków BTC.
- [ ] Zapisane transfery w `transfer_edge`.
- [ ] Endpoint health i podstawowe logowanie błędów.

## Sprint 2 (1 tydzień): API przepływów + pierwsza wizualizacja

### Zakres
- Endpoint `GET /flow/{chain}/{entity}` z filtrami.
- Zwracanie grafu: `nodes[]`, `edges[]`, metadane.
- Widok web: graf przepływów + filtry czasu/kwoty/hops.

### Kontrakt odpowiedzi (v0)
```json
{
  "chain": "btc",
  "entity": "bc1...",
  "nodes": [{"id": "addr:...", "type": "address"}],
  "edges": [{"id": "tx:...:0", "source": "addr:A", "target": "addr:B", "value": 1200000}],
  "meta": {"from": "2025-01-01", "to": "2025-01-31", "hops": 2}
}
```

### Definition of Done sprintu 2
- [ ] Endpoint zwraca poprawny graf dla BTC.
- [ ] UI renderuje graf i filtry działają.
- [ ] Obsługa pustych wyników i błędów.

## Sprint 3 (1 tydzień): użytkownicy i workspace (single + multiuser)

### Zakres
- Logowanie użytkownika.
- Workspace i członkowie workspace.
- Izolacja danych po `workspace_id`.

### Definition of Done sprintu 3
- [ ] Każdy użytkownik widzi tylko swoje workspace.
- [ ] Role: owner / analyst / viewer.
- [ ] Watchlista adresów BTC per workspace.

## Sprint 4 (1-2 tygodnie): ETH adapter + analiza kontraktów (v0)

### Zakres
- Ingest ETH tx + event logs.
- Transfery ERC-20 do `transfer_edge`.
- Moduł `contract_risk_signal`:
  - owner/admin,
  - proxy/upgradeability,
  - mint/pause/blacklist.

### Definition of Done sprintu 4
- [ ] Działa `GET /flow/eth/{entity}`.
- [ ] Widok przepływów tokenów ERC-20.
- [ ] Karta ryzyka kontraktu (v0) z listą sygnałów.


## Status realizacji
- ✅ Sprint 1: rozpoczęty (ingest BTC + model danych + health).
- ✅ Sprint 2: rozpoczęty (endpoint `GET /flow/{chain}/{entity}` + model odpowiedzi grafu).
- ✅ Sprint 3: rozpoczęty (workspace, role i watchlista per workspace).

## Priorytety (co robić najpierw, gdy czasu mało)
1. BTC ingest
2. API `/flow`
3. UI grafu
4. Workspace + role
5. ETH adapter

## Ryzyka i jak ograniczyć
- **Różne modele danych BTC/ETH** -> wspólny model `transfer_edge` + osobne adaptery.
- **Wydajność grafu** -> limity hops, agregacja małych edge, paginacja.
- **Koszt zapytań on-chain** -> cache i asynchroniczne joby.

## Checklist na najbliższe 48h
- [ ] Wybrać backend (FastAPI/NestJS).
- [ ] Rozpisać DDL v0.
- [ ] Dodać endpoint `GET /flow/{chain}/{entity}` jako stub.
- [ ] Przygotować mock danych BTC i wyrenderować pierwszy graf w UI.
