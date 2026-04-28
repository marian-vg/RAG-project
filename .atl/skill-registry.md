# Skill Registry

## Compact Rules

### Python Backend
- Use Pydantic models for configuration (`src/config.py`)
- Externalize prompts to `src/prompts.json` — never hardcode prompt strings
- Provider abstraction in `src/auditor.py` via `_get_llm()` factory

### React Frontend
- Vanilla CSS only for styling (no Tailwind component classes beyond what exists)
- Favicon and page title in `Views/index.html`

### Config Management
- All configuration changes via `src/config.py`
- Hot-reload supported via `/config` endpoint

## Project Standards

1. **Imports**: Use absolute imports from `src.` (e.g., `from src.auditor import...`)
2. **LLM Providers**: Ollama (local) or Gemini (cloud) — no other providers
3. **RAG**: LangChain 1.x + Chroma vectorstore
4. **PDF Ingestion**: Use `unstructured` library pipeline

## User Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `sdd-apply` | Implementation phase | Implement tasks from change |
| `sdd-explore` | Initial investigation | Investigate ideas before committing |
| `sdd-verify` | Validation | Validate implementation against specs |
| `sdd-archive` | Completion | Archive completed changes |

## Available Skills (from global registry)

### SDD Workflow
- `sdd-apply`, `sdd-archive`, `sdd-design`, `sdd-explore`, `sdd-init`, `sdd-propose`, `sdd-spec`, `sdd-tasks`, `sdd-verify`

### Utility
- `branch-pr`: PR creation workflow
- `issue-creation`: Issue creation workflow
- `judgment-day`: Parallel adversarial review
- `skill-creator`: Create new skills

### Language/Framework
- `langchain-fundamentals`, `langchain-rag`, `langchain-middleware`, `langchain-dependencies`
- `langgraph-fundamentals`, `langgraph-human-in-the-loop`, `langgraph-persistence`
- `deep-agents-core`, `deep-agents-memory`, `deep-agents-orchestration`
- `framework-selection`: Determine right framework for a task

## Detected Stack

- **Backend**: Python 3.x, FastAPI, LangChain 1.x, Chroma, Ollama, Gemini
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS 4, ESLint 9
- **Testing**: None detected