# API contracts

Base path: `/api/v1`

## Health

`GET /api/v1/health`

Response:

```json
{
  "status": "ok",
  "service": "tenderlens-backend",
  "environment": "development"
}
```

Errors use the following shape:

```json
{
  "code": "validation_error",
  "message": "The request contains invalid or missing fields.",
  "details": []
}
```

## Workspaces

`POST /api/v1/workspaces`

Request:

```json
{
  "title": "GeM tender review",
  "tender_reference": "GEM/2026/B/123",
  "organization_label": "Example MSME"
}
```

`GET /api/v1/workspaces` lists saved workspaces.

## Tender upload

`POST /api/v1/workspaces/{workspace_id}/documents`

Multipart field: `file`

The MVP accepts PDF files up to `MAX_UPLOAD_MB`. The response includes the generated document ID, page count, processing status
and extraction warnings. Full page text and source-linked chunks are available
through:

`GET /api/v1/documents/{document_id}`

Chunks are bounded text segments with `page_start`, `page_end`, `chunk_text`
and `chunk_type`. Candidate clauses are detected using deterministic cues such
as eligibility, turnover, certificates, deadlines, `shall`, `must` and
`required`. This discovery step does not claim that a clause is legally
mandatory or that a company is compliant.

## Requirements

`GET /api/v1/workspaces/{workspace_id}/requirements`

Returns source-linked, rule-extracted candidate requirements. Each item
contains its original clause, normalized text, category, mandatory status,
extracted value/unit where confidently available, extraction method,
confidence and a `review_required` flag. Rule extraction is a candidate
generation step; it is not a legal eligibility decision.

`PATCH /api/v1/requirements/{requirement_id}` updates reviewer-editable fields
and can set `confirmed_status` and `review_note`. The original
`source_clause_text` and source page are immutable. Suggested status and
reviewer-confirmed state remain separate.

## Structured provider boundary

The backend defaults to `LLM_PROVIDER=mock`, a deterministic free provider for
local development and tests. Provider output must validate against a structured
Pydantic schema and may reference only source chunks supplied by the
application. A paid provider is not required for the MVP.

## Evidence

`POST /api/v1/workspaces/{workspace_id}/evidence`

Uploads a company evidence PDF. Evidence documents are stored separately from
tenders and are not converted into tender requirements.

`POST /api/v1/requirements/{requirement_id}/match-evidence`

Retrieves ranked candidate evidence chunks from the workspace evidence library.
The response includes the retrieval score, matched terms, document name, page
number, source snippet and any deterministic rule reason. A retrieval score is
only a search signal and is never proof of compliance. Clear numeric and expiry
checks can suggest `evidence_found`; failed, missing or ambiguous checks remain
`needs_review`.

`PATCH /api/v1/evidence-matches/{match_id}`

Accepts `{ "user_status": "accepted" | "rejected" | "needs_review", "review_note": "..." }`.
Reviewer decisions are stored separately from `suggested_status`, preserving
the original automated result for auditability.

## Reports

`GET /api/v1/workspaces/{workspace_id}/report`

Returns an explainable compliance summary with counts and one row per
requirement. A requirement is only marked `compliant` after accepted evidence
or a clear rule result with completed requirement review. Amendment flags remain
`needs_review`.

`GET /api/v1/workspaces/{workspace_id}/report.csv`

Downloads the same requirement-level report as a CSV file for submission
preparation or spreadsheet review.

`GET /api/v1/workspaces/{workspace_id}/report.pdf`

Downloads a readable PDF summary generated locally with PyMuPDF. No paid
reporting or document service is required.

## Amendments

`POST /api/v1/workspaces/{workspace_id}/amendments`

Uploads an amendment as a separate immutable document.

`POST /api/v1/workspaces/{workspace_id}/compare-amendment?original_document_id={id}&amendment_document_id={id}`

Compares candidate clauses without overwriting the original tender. Changes
are classified as `added`, `changed`, `possibly_removed` or `unchanged`.
Potentially affected requirements are marked `re_review_required` and remain
available for human confirmation.

Uploaded files are stored under the configured private storage root using a
generated UUID filename. The original filename is metadata only.
