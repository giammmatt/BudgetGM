# Log — LLM Wiki

> Registro cronologico di tutte le operazioni atomiche sulla wiki. Ogni voce: timestamp ISO 8601, tipo, dettagli.

## Formato

```
## YYYY-MM-DD HH:MM
- [INGEST|UPDATE|DELETE|LINT|SYNTH] descrizione
  - file modificati: ...
  - fonte: raw/...
```

---

## 2026-05-08

- [INIT] Scaffolding della wiki.
  - file creati: `schema.md`, `index.md`, `log.md`, `.gitattributes`, `PLAN.md`
  - cartelle create: `raw/`, `wiki/{concepts,entities,sources,synthesis}/`, `presentations/`
