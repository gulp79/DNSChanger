# AGENTS.md — Ruoli & Regole
## Ruoli
- Manager: definisce piano, split in task, apre/chiude gate di review.
- Developer: implementa in branch feature con diff minimo e README aggiornato.
- Tester: crea/aggiorna test, verifica con browser-in-the-loop e allega screenshot/recording.

## Regole globali
1) Nessun merge in `main` senza gate Tester=PASS + Manager=APPROVE.
2) Ogni feature → Artifact "Implementation Plan" + diff circoscritto.
3) Preferire comandi PowerShell firmati o documentati (log in Artifacts).
4) Consentire terminale solo a comandi allowlist e domini browser whitelisted.

## Checklist missione
- [ ] Implementation Plan approvato
- [ ] UI: toggle “Encrypted DNS” + lista provider
- [ ] Log operazioni (PowerShell/servizio) salvati come Artifact
- [ ] Test funzionali + screenshot impostazioni Windows / output `netsh`