# GEMINI.md — Contesto progetto DNSChanger
## Stack
Python 3.x + CustomTkinter su Windows 11/Server 2025 (elevazione UAC già presente).

## Feature richiesta
Aggiungere supporto a DNS crittografati:
- DNS-over-HTTPS (DoH) di Windows 11/Server 2025

## Vincoli
- Nessuna modifica distruttiva alle funzioni DNS esistenti.
- Diff minimo e reversibile (toggle per Encrypted/Plain).
- Logging dettagliato e rollback facile a DHCP.
- Analisi performance e velocità di esecuzione, ottimizzazione.

## Accettazione
- Tutti i test passano; screenshot impostazioni Windows con DoH attivo; `netsh dns show encryption` coerente.