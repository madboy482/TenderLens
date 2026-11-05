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

## Demo deployment

The repository includes a demo deployment path with the React frontend on
Vercel and the FastAPI backend on Render.

### 1. Deploy the backend to Render

1. Push this repository to GitHub.
2. In Render, choose **New + > Blueprint** and select the repository.
3. Render will detect [`render.yaml`](./render.yaml) and build the backend from
   [`backend/Dockerfile`](./backend/Dockerfile).
4. After the service is created, copy its public URL, for example
   `https://tenderlens-api.onrender.com`.
5. In the Render service environment, set `FRONTEND_ORIGIN` to the final
   Vercel URL. For the first deployment, a temporary value can be used and
   updated after Vercel is created.

The API health check is:

```text
https://<render-service>.onrender.com/api/v1/health
```

### 2. Deploy the frontend to Vercel

1. In Vercel, import the same GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Use `npm run build` as the build command and `dist` as the output directory.
4. Add this environment variable:

```text
VITE_API_BASE_URL=https://<render-service>.onrender.com/api/v1
```

5. Deploy the site and copy its public URL.
6. Return to Render and set `FRONTEND_ORIGIN` to that Vercel URL, then
   redeploy the backend.

### Demo limitations

The included Render configuration uses SQLite and local file storage so the
MVP can be demonstrated without a database service. Render's free service
filesystem is not durable: database records and uploaded PDFs can disappear
after restarts or redeployments. For a real online deployment, move the
database to managed PostgreSQL and uploads to durable object storage (such as
Azure Blob Storage or S3-compatible storage) before storing user data.
