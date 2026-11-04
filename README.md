# TenderLens

TenderLens is a human-reviewed NLP and LLM-assisted tender compliance
assistant for Indian MSMEs. It extracts source-linked requirements from
tender documents, helps users find supporting company evidence, highlights
potential gaps, and produces a reviewable report.

## Project status

The project currently contains the local-first MVP workflow from the project
blueprint, including source-linked extraction, evidence review, amendment
impact analysis and explainable compliance reporting.

## Backend setup

From `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. OpenAPI documentation is
available at `http://localhost:8000/docs`.

Run backend tests with:

```powershell
pytest
```

## Frontend setup

From `frontend/`:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend runs at `http://localhost:5173` and checks the backend health
endpoint on startup. Run frontend tests and the production build with:

```powershell
npm test
npm run build
```

## Planned build order

1. Backend and frontend skeletons
2. PDF ingestion and page-level extraction (implemented)
3. Source-linked requirement extraction
4. Human review interface
5. Evidence retrieval and matching
6. Deterministic date and threshold checks
7. Amendment impact analysis
8. PDF/CSV reporting (implemented)
9. Evaluation set and documentation (baseline implemented)

The initial implementation is local-first and uses only free/open-source
tools. SQLite is used for local development, while the data layer will remain
portable to PostgreSQL for persistent deployment.

The backend defaults to a deterministic mock provider. No paid LLM API key is
required for local development or tests.

Run the deterministic NLP evaluation baseline from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m app.evaluation
```
