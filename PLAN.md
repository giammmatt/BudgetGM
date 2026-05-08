# Piano di implementazione — LLM Wiki

## Fase 0 — Scaffolding (DONE)
- [x] Branch `claude/llm-wiki-setup`
- [x] Struttura cartelle
- [x] `schema.md`, `index.md`, `log.md`, `.gitattributes`, `PLAN.md`

## Fase 1 — Setup cloud & accesso multi-device
- [ ] Push del branch su GitHub
- [ ] (Opzionale) Migrare la wiki in repo dedicata `llm-wiki` (consigliato)
- [ ] Attivare Git LFS sul repo (`git lfs install` locale + `git lfs track` già configurato)
- [ ] Repo privato — verificare visibilità
- [ ] Setup PC: clone repo + Obsidian con plugin "Obsidian Git" puntato alla cartella
- [ ] Setup mobile:
  - iOS: Working Copy + Obsidian mobile (vault sulla cartella di Working Copy)
  - Android: Termux + git, oppure app GitHub + Obsidian con sync manuale

## Fase 2 — Primo ingest
- [ ] Caricare in `raw/` i materiali iniziali (PDF dei piani, screenshot, note)
- [ ] Sessione Claude Code con prompt: "Esegui l'ingest dei file in raw/ seguendo schema.md"
- [ ] Review delle note generate
- [ ] Commit & push

## Fase 3 — Routine operativa
- [ ] Definire frequenza di ingest (es. settimanale)
- [ ] Definire frequenza di linting (es. mensile)
- [ ] (Opzionale) Sviluppare CLI custom per ricerca interna alla wiki

## Fase 4 — Output & visualizzazione
- [ ] Generare prima presentazione MARP da contenuti wiki
- [ ] Esplorare grafo dei backlink in Obsidian
- [ ] (Avanzato) Esportare snapshot della wiki come bundle per query offline

## Decisioni aperte

1. **Repo dedicata vs branch in BudgetGM?**
   Raccomandazione: **repo dedicata** `llm-wiki` privata. BudgetGM è un bot Telegram, mescolare i due crea confusione. Questo branch serve come prototipo: una volta validato, copio i file in una nuova repo e cancello il branch.

2. **Cosa va in `raw/`?**
   Da decidere insieme: piani di allenamento, log delle sessioni, screenshot di app fitness, articoli scientifici, video trascritti?

3. **Lingua delle note**: italiano (default) o inglese? Impatta la coerenza terminologica.
