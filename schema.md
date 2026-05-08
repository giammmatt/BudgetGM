# LLM Wiki — Schema & Direttive Operative

> File di "skill" letto dall'agente AI a ogni sessione. Contiene le regole di comportamento per la gestione della wiki.

## Obiettivo

Mantenere una base di conoscenza personale in Markdown, navigabile via backlink Obsidian-style, su cui l'AI possa fare ingest, query, sintesi e linting.

## Struttura del filesystem

```
/
├── raw/              # Dati grezzi non processati (PDF, CSV, trascrizioni, clipping web, immagini)
├── wiki/
│   ├── concepts/     # Definizioni e principi teorici
│   ├── entities/     # Persone, aziende, tool, oggetti
│   ├── sources/      # Riassunti strutturati dei documenti originali (con metadati YAML)
│   └── synthesis/    # Output complessi di query cross-source
├── presentations/    # Slide MARP
├── index.md          # Mappa concettuale e punto di ingresso
├── log.md            # Registro cronologico di ingest/modifiche/eliminazioni
└── schema.md         # Questo file
```

## Convenzioni

- **Backlink**: usa `[[NomePagina]]` per i collegamenti interni (compatibile Obsidian).
- **Frontmatter YAML** obbligatorio in ogni nota di `wiki/sources/`:
  ```yaml
  ---
  title: ...
  type: paper | article | video | book | dataset | note
  source_path: raw/...
  ingested: YYYY-MM-DD
  tags: [...]
  ---
  ```
- **Naming**: kebab-case per i file (`peak-power-output.md`).
- **Lingua**: italiano per le note personali, inglese se la fonte lo è (manteniamo coerenza con la fonte).

## Workflow

### 1. Ingest
Quando l'utente aggiunge file in `raw/`:
1. Analizza il contenuto.
2. Estrai entità e concetti chiave.
3. Crea/aggiorna note in `wiki/sources/` (riassunto strutturato + frontmatter).
4. Crea/aggiorna note in `wiki/concepts/` e `wiki/entities/` per i concetti emersi.
5. Inserisci backlink `[[...]]` ovunque rilevante.
6. Aggiorna `index.md` se nasce un nuovo cluster tematico.
7. Registra l'azione in `log.md` con timestamp.

### 2. Query
Per ogni domanda dell'utente:
1. Parti da `index.md`.
2. Naviga i backlink per raccogliere il contesto.
3. Rispondi citando i file interni (`wiki/concepts/foo.md`).
4. Se la risposta apporta valore nuovo, proponi di salvarla in `wiki/synthesis/`.

### 3. Linting
Health check periodico:
- Pagine candidate (link a note inesistenti).
- Inconsistenze tra fonti.
- Cluster ridondanti da unire.
- Note orfane (senza backlink in entrata).

## Direttive di comportamento

- L'AI è un **curatore attivo**, non un motore di ricerca passivo.
- Coerenza terminologica obbligatoria.
- Ogni affermazione deve poter essere ritracciata a una fonte interna.
- Mai modificare manualmente le note senza loggare l'azione.
