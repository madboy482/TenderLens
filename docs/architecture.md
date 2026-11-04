# TenderLens architecture

TenderLens uses a local-first modular architecture:

```text
React frontend -> FastAPI API -> services/NLP -> repositories -> SQLite
                                      |
                                      +-> private local document storage
```

The backend is separated into API, service, NLP, persistence and storage
layers. API routes validate requests and delegate work; NLP modules preserve
source references; deterministic application code validates dates, thresholds,
files and state transitions.

The first implementation uses SQLite locally. SQLAlchemy will provide the
database abstraction needed to use PostgreSQL for a persistent deployment
without changing business logic.
