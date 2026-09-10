# EU MDR Regulatory Intelligence System

A retrieval-augmented question-answering system over **Regulation (EU) 2017/745** (Medical Device Regulation). It ingests the official PDF, rebuilds its legal structure (Chapters → Articles → Annexes → paragraphs), chunks it with that structure preserved, and answers questions with **verifiable citations** back to article and page.

> **Status:** in active development — ingestion and structure-aware chunking are working; embeddings, vector store, retrieval and generation are next.

<!-- TODO: add a demo GIF / screenshot here once there's a UI -->

---

## Why this exists

<!-- TODO: 3–4 lines in your own words. Suggested angle: -->
MDR compliance questions ("what does a manufacturer have to do under Article 10?") are answered today by manually searching a 175-page regulation. A generic LLM will answer them fluently and sometimes wrongly. This system constrains answers to retrieved regulation text and validates every citation it emits.

---

## Pipeline status

| Stage | Module | Status |
|---|---|---|
| PDF extraction (table-aware) | `src/ingestion/pdf_extractor.py` | ✅ Done |
| Structure parsing (Chapter/Article/Annex/Section) | `src/ingestion/structure_parser.py` | ✅ Done |
| Text cleaning | `src/ingestion/text_cleaner.py` | ✅ Done |
| Structure-aware chunking | `src/chunking/chunker.py` | ✅ Done |
| Embeddings (`BAAI/bge-base-en-v1.5`) | `src/embeddings/` | 🚧 In progress |
| Vector store (ChromaDB) | `src/vector_store/` | ⬜ Not started |
| Retrieval | `src/retrieval/` | ⬜ Not started |
| Generation + prompting | `src/generation/`, `src/prompts/` | ⬜ Not started |
| Citation validation | `extra_curricular.py` (prototype) | 🚧 Prototype |
| Knowledge graph (Neo4j) | `src/knowledge_graph/` | ⬜ Not started |
| Evaluation | `src/evaluation/` | ⬜ Not started |
| UI | <!-- TODO --> | ⬜ Not started |

Legend: ✅ done · 🚧 in progress · ⬜ not started

---

## How it works

```
data/raw/*.pdf
      │
      ▼
PDF_Extractor        pymupdf; detects tables, caches their bboxes to
                     data/cache/tables.json, then extracts only the text
                     blocks that do NOT intersect a table
      │  raw_text, page_starts
      ▼
Structure_Parser     regex markers rebuild the legal hierarchy:
                     ANNEX [IVX]+ · CHAPTER [IVX]+ · SECTION \d+ · Article \d+
      │  document map
      ▼
Text_Cleaner         normalises whitespace / artefacts → cleaned JSON in
                     data/processed/cleaned_<name>.json
      │
      ▼
Chunker              splits within structural units, max 512 tokens
                     (tokenizer = the embedding model's), numbering patterns:
                     1. · 1.1. · 1.1.1. · (a) · (1) · —
      │  chunks + metadata
      ▼
[embeddings → vector store → retrieval → generation]   ← next up
```

### Chunk metadata schema

Every chunk carries the provenance needed to cite it:

| Field | Type | Nullable | Example |
|---|---|---|---|
| `document_name` | str | No | `eu_mdr_2017-745` |
| `document_type` | str | No | `regulation` |
| `chapter` | str | Yes | `Chapter II` |
| `article_number` | str | Yes | `Article 10` |
| `article_title` | str | Yes | `General obligations of manufacturers` |
| `annex` | str | Yes | `Annex VIII` |
| `section_header` | str | Yes | `Classification Rules` |
| `paragraph_number` | str | Yes | `(3)(a)` |
| `page_number` | int | No | `31` |
| `cross_references` | list[str] | Yes | `["Article 10(3)", "Annex XIV"]` |

---

## Quickstart

```bash
git clone https://github.com/vrjbhvsr/EU_MDR_RAG.git
cd EU_MDR_RAG

# macOS / Linux
conda env create -f environment.yml
# Windows
conda env create -f environment_win.yml

conda activate eu-mdr
pip install -e .
```

Put the regulation PDF in `data/raw/` (git-ignored):

```bash
mkdir -p data/raw data/processed data/cache
# download Regulation (EU) 2017/745 → data/raw/eu_mdr_2017-745.pdf
```

Run the pipeline end to end:

```bash
python main.py
```

This ingests every PDF in `data/raw/`, writes `data/processed/cleaned_<name>.json`, chunks it, and prints the first chunk.

**Requirements:** Python 3.11+ · chromadb 1.5.7 · pymupdf 1.27.2 · sentence-transformers 5.3.0 · unstructured 0.22.22

---

## Configuration

All settings live in `config/settings.py` (pydantic-settings). Override with a `.env` file using the nested delimiter `__`:

```env
INGESTION__RAW_DATA_DIR=data/raw
EMBEDDING__MODEL_NAME=BAAI/bge-base-en-v1.5
CHUNKING__MAX_TOKENS=512
```

| Group | Key | Default |
|---|---|---|
| `ingestion` | `raw_data_dir` / `processed_data_dir` / `cache_dir` | `data/raw` · `data/processed` · `data/cache` |
| `embedding` | `model_name` | `BAAI/bge-base-en-v1.5` |
| `chunking` | `max_tokens` | `512` |
| `chunking` | `patterns`, `marker_patterns` | see `settings.py` |

---

## Repository layout

```
config/          pydantic settings (ingestion, embedding, chunking)
scripts/         Document_Ingestor — orchestrates extract → parse → clean
src/
  ingestion/     pdf_extractor · structure_parser · text_cleaner
  chunking/      structure-aware Chunker
  embeddings/    (stub)
  vector_store/  (stub)
  retrieval/     (stub)
  generation/    (stub)
  knowledge_graph/ (stub)
  evaluation/    (stub)
  utils/         colorlog logger → Bug_Tracker/logs/app.log · CustomException
Prompts/         prompt iterations (prompt.md … prompt_5.md)
main.py          end-to-end run
```

Logging: `src/utils/logger.py` writes to `Bug_Tracker/logs/app.log` and mirrors to console with per-level colours. Errors are wrapped in `CustomException` with the originating file and line.

---

## Design decisions

<!-- TODO: keep adding as you make them — this is the section that makes the repo interesting -->

- **Tables are excluded from the text stream, not flattened.** `pymupdf` finds table bounding boxes first; text blocks that intersect them are skipped and the tables are cached separately as markdown in `data/cache/tables.json`. Flattened tables destroy the classification rules in Annex VIII.
- **Chunk on legal structure, not on character count.** An Article is a semantic unit; splitting mid-paragraph loses the subject of the obligation.
- **Citations are validated, not trusted.** `citation_validator` re-extracts identifiers from the model's answer, matches them against the retrieved chunks (full match first, page number as fallback anchor) and marks anything unmatched `[Unverified: …]`.

---

## Roadmap

- [x] Table-aware PDF extraction
- [x] Structure parsing for Chapters / Articles / Annexes / Sections
- [x] Text cleaning + processed JSON output
- [x] Structure-aware chunking with token budget
- [ ] Embed chunks with `bge-base-en-v1.5`
- [ ] Persist to ChromaDB with metadata filters
- [ ] Hybrid retrieval (dense + metadata filter on chapter/article/annex)
- [ ] Answer generation with enforced citation format
- [ ] Wire `citation_validator` into the generation loop
- [ ] Cross-reference knowledge graph in Neo4j
- [ ] Evaluation set + retrieval/answer metrics
- [ ] Streamlit UI
<!-- TODO: add / tick items as you go -->

---

## Changelog

<!-- TODO: one line per working session. Newest first. -->

| Date | Change |
|---|---|
| _YYYY-MM-DD_ | _e.g. Added Chunker with 512-token budget_ |

---

## License

<!-- TODO: pick one (MIT is the usual default) -->

## Acknowledgements

Source text: Regulation (EU) 2017/745 of the European Parliament and of the Council, published by EUR-Lex. This project is an independent engineering exercise and is **not** legal advice or a compliance tool.
