# AGENTS.md — FarmaRAG

## Project Overview

**Project**: FarmaRAG — Farmacy Auditor RAG Chatbot
**Type**: RAG (Retrieval-Augmented Generation) chatbot for pharmacy regulation auditing
**Stack**: Python FastAPI + Svelte 5 (migrated from React)
**Artifact Store**: engram

---

## Architecture

```
Frontend (Svelte:5173) → FastAPI (server.py:8000) → FarmaRAG (unificador.py)
                                                          ↓
                                                   FarmaAuditor (auditor.py)
                                                          ↓
                                       Chroma DB ← HuggingFaceEmbeddings
                                                          ↓
                                       LLM: Ollama (local) / Gemini (cloud)
```

---

## Skills

### SDD Workflow
| Skill | Trigger | Description |
|-------|---------|-------------|
| `sdd-init` | Project start | Bootstrap SDD context |
| `sdd-propose` | New change | Create proposal document |
| `sdd-spec` | Proposal approved | Write detailed specifications |
| `sdd-design` | Spec approved | Technical design document |
| `sdd-tasks` | Design approved | Implementation task breakdown |
| `sdd-apply` | Tasks ready | Implement code changes |
| `sdd-verify` | Implementation done | Validate against specs |
| `sdd-archive` | Change completed | Sync delta specs to main |

### Language/Framework
| Skill | Use When |
|-------|----------|
| `langchain-fundamentals` | Using LangChain primitives |
| `langchain-rag` | Building RAG pipelines |
| `langchain-middleware` | Human-in-the-loop, custom middleware |
| `langchain-dependencies` | Package versions, installation |
| `langgraph-fundamentals` | LangGraph workflow design |
| `langgraph-human-in-the-loop` | Interrupt patterns, approval flows |
| `langgraph-persistence` | Checkpointing, memory, time travel |
| `framework-selection` | Choosing between LangChain/LangGraph/Deep Agents |

### Utility
| Skill | Use When |
|-------|----------|
| `judgment-day` | Adversarial review |
| `branch-pr` | Pull request workflow |
| `skill-creator` | Creating new skills |

---

## Artifact Store

**Mode**: `engram`
**Location**: Memory persistence via engram_mem_* functions

```
sdd/{project}/proposal     → Proposal documents
sdd/{project}/spec         → Detailed specifications
sdd/{project}/design       → Technical designs
sdd/{project}/tasks        → Implementation task lists
sdd/{project}/apply-progress → Progress tracking
sdd-init/{project}          → Project initialization context
{farmaRAG/iteration-2-requirements} → Deferred work notes
```

---

## Project Conventions

### Backend (Python)
- **Configuration**: Pydantic models in `src/config.py`
- **Prompts**: Externalized to `src/prompts.json`
- **Provider Factory**: `src/auditor.py::_get_llm()` abstracts Ollama/Gemini
- **Error Handling**: Custom exceptions (`LLMProviderError`, `LLMRateLimitError`, etc.)
- **Imports**: Absolute imports from `src.` (e.g., `from src.auditor import...`)

### Frontend (Svelte 5)
- **State Management**: Svelte 5 runes (`$state`, `$effect`, `$props`, `$bindable`)
- **Notifications**: Toast system via `src/lib/toast.ts` store
- **Icons**: `lucide-svelte`
- **Markdown**: `marked` library
- **Styling**: Tailwind CSS v4 with `@tailwindcss/typography`

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health check + engine status |
| `POST` | `/ask` | Query RAG with fallback support |
| `POST` | `/config` | Hot-swap model/provider |
| `GET` | `/fallback-status` | Last fallback event info |

---

## Iteration 2 Status

### Completed (Fase 1)
- ✅ Timeout en Ollama (30s)
- ✅ Exception handling robusto
- ✅ Fallback automático backend
- ✅ Toast notifications (success/warning/error)
- ✅ FAQ cards muestran pregunta en chat
- ✅ Debounce en cambios de configuración (500ms)

### Planned (Fase 2: Security)
- Input sanitization (prompt injection prevention)
- Rate limiting (10 req/min per IP)
- CORS configuration (keep `*` for dev)

### Planned (Fase 3: Observability)
- Structured logging (JSON with request_id)
- Deep health check (`/health` endpoint)

### Planned (Fase 4: Robustness)
- Circuit breaker
- Dead letter logging

---

## Detected Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.x, FastAPI, LangChain 1.x, Chroma |
| **LLM Providers** | Ollama (local), Gemini (cloud) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` |
| **Frontend** | Svelte 5, TypeScript, Vite, Tailwind v4 |
| **Frontend Icons** | lucide-svelte |
| **Frontend Markdown** | marked |
| **Error Handling** | tenacity (retry), custom exceptions |
| **Testing** | ✅ pytest (`pytest>=7.0`) |

---

## Testing Capabilities

| Capability | Status |
|------------|--------|
| Test Runner | ✅ pytest |
| Unit Tests | ✅ `tests/unit-tests/` |
| Integration Tests | ✅ `tests/integration-tests/` |
| Config Tests | ✅ `tests/config-tests/` |
| Scripts Tests | ✅ `tests/scripts-tests/` |
| Linter | ✅ ESLint 9.x (`npm run lint`) |
| Type Checker | ✅ TypeScript (`tsc --noEmit`) |

---

## Rules

1. **Backend changes** → Python files in `src/` (auditor.py, unificador.py, config.py, etc.)
2. **Frontend changes** → Svelte files in `Views/src/`
3. **Config persistence** → JSON file at project root (`config.json`)
4. **Prompts externalized** → `src/prompts.json`
5. **No hardcoded prompts** → Always load from file with fallback
6. **Provider abstraction** → `_get_llm()` factory in auditor.py
7. **Error classification** → Use custom exceptions, not string matching
8. **Fallback logic** → `ask_with_fallback()` tries providers in order, returns metadata
9. **Toast dedup** → Config change debounce 500ms + only show if really changed

---

## Index

```
/
├── server.py              # FastAPI app
├── config.json            # Runtime config (JSON persistence)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── AGENTS.md              # This file
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── auditor.py          # RAG chain + LLM factory + exceptions
│   ├── unificador.py      # FarmaRAG facade
│   ├── config.py           # FarmaConfig Pydantic model
│   ├── procesador.py       # PDF ingestion + entity detection
│   └── prompts.json       # Prompt templates
├── Views/                  # Svelte frontend
│   ├── package.json
│   └── src/
│       ├── App.svelte      # Main app component
│       ├── main.ts         # Entry point
│       ├── app.css         # Global styles
│       ├── lib/
│       │   └── toast.ts    # Toast notification store
│       ├── components/
│       │   ├── Sidebar.svelte
│       │   ├── ChatWindow.svelte
│       │   ├── FAQCards.svelte
│       │   └── Toast.svelte
│       └── assets/
│           └── hero.png
├── scripts/                # Utility scripts
│   ├── ingesta.py
│   ├── farma_query.py
│   ├── listar_modelos.py
│   └── test_rag.py
├── docs/                   # Documentation
│   ├── README.md
│   ├── ERRORS.md
│   └── RESUME.md
├── logs/                   # Runtime logs + dead letter
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest fixtures
│   ├── test_data.py        # FAQ queries + synthetic queries
│   ├── results_logger.py   # JSON audit logger
│   ├── config-tests/       # Parameter variation tests
│   ├── integration-tests/  # Flow tests
│   ├── unit-tests/         # Isolated component tests
│   └── scripts-tests/      # Scripts validation tests
├── .agents/               # Agent skills (OpenSpec format)
├── .atl/                  # Agent Teams Lite config
└── .env                   # Environment variables
```