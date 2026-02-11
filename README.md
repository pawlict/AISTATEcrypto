# AISTATEcrypto

## MVP: analiza przepływów i smart kontraktów (BTC + ETH)

### Czy start od BTC zmienia plan?
Tak — ale głównie **warstwę danych i analityki**, a nie frontend czy model użytkowników.

- **BTC** to model UTXO (wejścia/wyjścia transakcji, brak smart kontraktów jak w EVM).
- **ETH** to model kontowy (account-based), zdarzenia kontraktów, tokeny ERC-20/721, ABI, proxy itp.

Najlepiej budować wspólną platformę z dwoma adapterami łańcuchów:

1. `chain-adapter-btc` — parser transakcji UTXO + heurystyki adresowe/klastrowanie.
2. `chain-adapter-eth` — parser tx/event logs + analiza smart kontraktów.

Dzięki temu aplikacja webowa, role użytkowników i dashboardy pozostają wspólne.

## Rekomendowany etapowy plan

### Etap 1 (BTC-first, 3–4 tygodnie)
- Ingest danych BTC (blok, tx, input/output, fee, czas).
- Normalizacja do wspólnego modelu `TransferEdge`.
- Graf przepływów dla adresu/clusteru z filtrami (czas, kwota, hops).
- Alerty podstawowe:
  - duże wypływy,
  - nagłe zwiększenie aktywności,
  - kontakty z oznaczonymi adresami.

### Etap 2 (ETH add-on, 3–5 tygodni)
- Ingest ETH tx + event logs (w tym ERC-20 Transfer).
- Widok token flow (transfery tokenów między adresami).
- Podstawowa analiza kontraktów:
  - owner/admin,
  - proxy/upgradeability,
  - mint/pause/blacklist funkcje.

### Etap 3 (multiuser + operacjonalizacja)
- Workspace i role: Owner / Analyst / Viewer.
- Watchlisty per workspace.
- Współdzielone dashboardy i alerty.

## Co jest wspólne dla BTC i ETH
- Frontend web (np. Next.js + TypeScript).
- Silnik grafowy (np. Cytoscape.js / Sigma).
- Zarządzanie użytkownikami i tenantami (workspace_id).
- System alertów i harmonogramy zadań.

## Co jest różne (i trzeba to uwzględnić)
- **Model danych łańcucha**: UTXO vs account.
- **Semantyka przepływów**: BTC input/output vs ETH value + token events.
- **Analiza kontraktów**: praktycznie tylko ETH/EVM.

## Minimalny model domenowy (pod oba łańcuchy)
- `User`
- `Workspace`
- `WorkspaceMember`
- `TrackedEntity` (address / contract / cluster)
- `ChainTransaction`
- `TransferEdge`
- `AlertRule`
- `AlertEvent`
- `ContractRiskSignal` (używane dla ETH)

## Proponowany stack
- Frontend: Next.js + TypeScript.
- Backend API: FastAPI lub NestJS.
- Przetwarzanie: kolejka Redis + worker.
- DB transakcyjna: PostgreSQL.
- Duże wolumeny/analityka: ClickHouse (opcjonalnie na później).

## Pierwsze 5 zadań implementacyjnych
1. Zdefiniować kontrakt API dla endpointu `/flow/:chain/:entity`.
2. Uruchomić BTC ingest i zapisać do `ChainTransaction` + `TransferEdge`.
3. Wyrenderować graf przepływów BTC w UI.
4. Dodać logowanie + workspace (single-user ready, multiuser-capable).
5. Dodać adapter ETH i pierwszy widok token transferów.

## Odpowiedź na pytanie „BTC najpierw, potem ETH — czy to zmienia plan?”
- **Tak, kolejność prac się zmienia**: najpierw moduł UTXO i heurystyki BTC.
- **Nie, architektura produktu nie musi się zmieniać**: projektuj od początku jako multi-chain + multiuser.
- **Największy zysk**: szybciej dowozisz działające grafy przepływów (BTC), a smart-kontrakty dokładasz jako osobny moduł ETH.

## Co dalej (praktycznie)
Jeśli chcesz zacząć od razu implementację, przejdź do checklisty i planu sprintów w `docs/NEXT_STEPS.md`.

## Status implementacji
- ✅ Etap 1 został rozpoczęty w katalogu `backend/` (model danych, ingest BTC, health endpoint, CLI sync).
- Szczegóły uruchomienia i zakres znajdują się w `backend/README.md`.
