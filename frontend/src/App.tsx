import { useEffect, useState, type FormEvent } from 'react'
import {
  createWorkspace,
  compareAmendment,
  getDocument,
  getHealth,
  getRequirements,
  getReport,
  getReportCsvUrl,
  getReportPdfUrl,
  matchEvidence,
  uploadEvidence,
  uploadAmendment,
  updateEvidenceMatch,
  updateRequirement,
  uploadTender,
  type Document,
  type DocumentDetail,
  type HealthResponse,
  type Requirement,
  type EvidenceMatch,
  type AmendmentChange,
  type ComplianceSummary,
} from './api/client'
import './App.css'

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [workspaceTitle, setWorkspaceTitle] = useState('')
  const [workspaceId, setWorkspaceId] = useState<string | null>(null)
  const [document, setDocument] = useState<Document | null>(null)
  const [documentDetail, setDocumentDetail] = useState<DocumentDetail | null>(null)
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [actionError, setActionError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [evidenceBusy, setEvidenceBusy] = useState(false)
  const [evidenceStatus, setEvidenceStatus] = useState<string | null>(null)
  const [matches, setMatches] = useState<Record<string, EvidenceMatch[]>>({})
  const [amendment, setAmendment] = useState<Document | null>(null)
  const [amendmentChanges, setAmendmentChanges] = useState<AmendmentChange[]>([])
  const [report, setReport] = useState<ComplianceSummary | null>(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setError('Backend is unavailable. Start the FastAPI server to connect.'))
  }, [])

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const file = form.get('tender') as File
    if (!workspaceTitle.trim() || !file?.name) {
      setActionError('Enter a workspace name and choose a PDF.')
      return
    }

    setBusy(true)
    setActionError(null)
    try {
      const workspace = await createWorkspace(workspaceTitle.trim())
      setWorkspaceId(workspace.id)
      const uploaded = await uploadTender(workspace.id, file)
      setDocument(uploaded)
      setDocumentDetail(await getDocument(uploaded.id))
      setRequirements(await getRequirements(workspace.id))
    } catch (uploadError) {
      setActionError(uploadError instanceof Error ? uploadError.message : 'Upload failed.')
    } finally {
      setBusy(false)
    }

  }

  async function confirmRequirement(requirement: Requirement) {
    try {
      const updated = await updateRequirement(requirement.id, {
        confirmed_status: 'reviewed',
        review_note: 'Reviewed by user.',
      })
      setRequirements((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      )
    } catch (reviewError) {
      setActionError(reviewError instanceof Error ? reviewError.message : 'Could not save review.')
    }

  }

  async function handleEvidenceUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const file = new FormData(event.currentTarget).get('evidence') as File
    if (!workspaceId || !file?.name) {
      setActionError('Choose an evidence PDF after uploading a tender.')
      return
    }
    setEvidenceBusy(true)
    setActionError(null)
    try {
      const uploaded = await uploadEvidence(workspaceId, file)
      setEvidenceStatus(`Uploaded ${uploaded.original_name}. Evidence is ready for matching.`)
    } catch (uploadError) {
      setActionError(uploadError instanceof Error ? uploadError.message : 'Evidence upload failed.')
    } finally {
      setEvidenceBusy(false)
    }
  }

  async function handleMatch(requirement: Requirement) {
    try {
      setEvidenceStatus(`Searching evidence for page ${requirement.source_page_start} requirement...`)
      const results = await matchEvidence(requirement.id)
      setMatches((current) => ({ ...current, [requirement.id]: results }))
      setEvidenceStatus(results.length ? `Found ${results.length} candidate evidence match(es).` : 'No candidate evidence found.')
    } catch (matchError) {
      setActionError(matchError instanceof Error ? matchError.message : 'Evidence matching failed.')
    }
  }

  async function reviewEvidenceMatch(
    requirementId: string,
    match: EvidenceMatch,
    userStatus: EvidenceMatch['user_status'],
  ) {
    if (!userStatus) return
    try {
      const updated = await updateEvidenceMatch(match.id, {
        user_status: userStatus,
        review_note: match.review_note,
      })
      setMatches((current) => ({
        ...current,
        [requirementId]: (current[requirementId] ?? []).map((item) =>
          item.id === updated.id ? updated : item,
        ),
      }))
    } catch (reviewError) {
      setActionError(reviewError instanceof Error ? reviewError.message : 'Could not save evidence review.')
    }
  }

  async function annotateEvidenceMatch(requirementId: string, match: EvidenceMatch) {
    try {
      const updated = await updateEvidenceMatch(match.id, {
        user_status: match.user_status ?? 'needs_review',
        review_note: match.review_note,
      })
      setMatches((current) => ({
        ...current,
        [requirementId]: (current[requirementId] ?? []).map((item) =>
          item.id === updated.id ? updated : item,
        ),
      }))
    } catch (reviewError) {
      setActionError(reviewError instanceof Error ? reviewError.message : 'Could not save evidence note.')
    }
  }

  async function handleAmendmentUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const file = new FormData(event.currentTarget).get('amendment') as File
    if (!workspaceId || !document?.id || !file?.name) {
      setActionError('Upload a tender before adding an amendment.')
      return
    }

    setEvidenceBusy(true)
    setActionError(null)
    try {
      const uploaded = await uploadAmendment(workspaceId, file)
      setAmendment(uploaded)
      const changes = await compareAmendment(workspaceId, document.id, uploaded.id)
      setAmendmentChanges(changes)
      setRequirements(await getRequirements(workspaceId))
      setEvidenceStatus(`${changes.filter((change) => change.change_type !== 'unchanged').length} amendment change(s) require review.`)
    } catch (amendmentError) {
      setActionError(amendmentError instanceof Error ? amendmentError.message : 'Amendment comparison failed.')
    } finally {
      setEvidenceBusy(false)
    }
  }

  async function loadReport() {
    if (!workspaceId) return
    try {
      setReport(await getReport(workspaceId))
    } catch (reportError) {
      setActionError(reportError instanceof Error ? reportError.message : 'Could not load report.')
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">T</span>
          <span>TenderLens</span>
        </div>
        <span className="eyebrow">Tender compliance intelligence</span>
      </header>

      <section className="hero">
        <p className="eyebrow">Workspace overview</p>
        <h1>Prepare bids with clarity.</h1>
        <p className="hero-copy">
          TenderLens turns complex tender documents into source-linked requirements,
          evidence matches and reviewable compliance findings.
        </p>
        <div className="status-card" aria-live="polite">
          <span className={`status-dot ${health ? 'online' : ''}`} />
          <div>
            <strong>{health ? 'Backend connected' : error ? 'Backend not connected' : 'Connecting...'}</strong>
            <p>{health ? `${health.service} · ${health.environment}` : error ?? 'Checking the local API health endpoint.'}</p>
          </div>
        </div>
      </section>

      <section className="feature-grid" aria-label="TenderLens workflow">
        <article>
          <span className="feature-number">01</span>
          <h2>Upload a tender</h2>
          <p>Extract tender pages while preserving the source references needed for review.</p>
        </article>
        <article>
          <span className="feature-number">02</span>
          <h2>Review requirements</h2>
          <p>Organize eligibility, financial, technical and documentary requirements.</p>
        </article>
        <article>
          <span className="feature-number">03</span>
          <h2>Check evidence</h2>
          <p>Match company documents and highlight missing or ambiguous evidence.</p>
        </article>
      </section>

      <section className="upload-panel">
        <div>
          <p className="eyebrow">Start a workspace</p>
          <h2>Upload your first tender</h2>
          <p>Text-based PDFs are supported now. Scanned pages are marked for OCR review.</p>
        </div>
        <form onSubmit={handleUpload}>
          <label>
            Workspace name
            <input
              value={workspaceTitle}
              onChange={(event) => setWorkspaceTitle(event.target.value)}
              placeholder="Example: GeM tender review"
            />
          </label>
          <label>
            Tender PDF
            <input name="tender" type="file" accept="application/pdf,.pdf" />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Processing...' : 'Upload tender'}
          </button>
          {actionError && <p className="form-error">{actionError}</p>}
          {document && (
            <p className="upload-success">
              Uploaded {document.original_name}: {document.page_count} page(s) extracted.
              {workspaceId && ` Workspace ${workspaceId.slice(0, 8)}...`}
            </p>
          )}
        </form>
      </section>

      {documentDetail && (
        <section className="extraction-panel">
          <div>
            <p className="eyebrow">Extraction preview</p>
            <h2>Source-linked candidate clauses</h2>
            <p>
              Candidate clauses are discovery signals, not compliance decisions.
              Every item retains its source page for later review.
            </p>
          </div>
          <div className="chunk-list">
            {documentDetail.chunks.filter((chunk) => chunk.chunk_type === 'candidate_clause').map((chunk) => (
              <article className="chunk-card" key={chunk.id}>
                <span>Page {chunk.page_start}</span>
                <p>{chunk.chunk_text}</p>
              </article>
            ))}
            {documentDetail.chunks.filter((chunk) => chunk.chunk_type === 'candidate_clause').length === 0 && (
              <p className="empty-copy">No candidate clauses were detected in the extracted text.</p>
            )}

          </div>
          {documentDetail.warnings.length > 0 && (
            <div className="warning-box">
              {documentDetail.warnings.map((warning) => <p key={warning}>{warning}</p>)}
            </div>
          )}
        </section>
      )}

      {requirements.length > 0 && (
        <section className="requirements-panel">
          <div className="requirements-heading">
            <div>
              <p className="eyebrow">Review queue</p>
              <h2>Extracted requirements</h2>
            </div>
            <span>{requirements.length} candidate requirement(s)</span>
          </div>
          <div className="requirements-list">
            {requirements.map((requirement) => (
              <article className="requirement-card" key={requirement.id}>
                <div className="requirement-meta">
                  <span>{requirement.category}</span>
                  <span>Page {requirement.source_page_start}</span>
                  <span>{requirement.mandatory_status}</span>
                </div>
                <h3>{requirement.normalized_text}</h3>
                <blockquote>{requirement.source_clause_text}</blockquote>
                <div className="requirement-values">
                  <span>Suggested: {requirement.suggested_status}</span>
                  <span>{requirement.review_required ? 'Review required' : 'Reviewed'}</span>
                  {requirement.extracted_value && <span>Value: {requirement.extracted_value}</span>}
                </div>
                {requirement.review_required && (
                  <button type="button" className="review-button" onClick={() => confirmRequirement(requirement)}>
                    Mark as reviewed
                  </button>
                )}
                <button type="button" className="review-button" onClick={() => handleMatch(requirement)}>
                  Find evidence
                </button>
                {matches[requirement.id]?.map((match) => (
                  <div className="evidence-match" key={match.id}>
                    <strong>{match.evidence_document_name} · Page {match.evidence_page_start}</strong>
                    <p>{match.evidence_snippet}</p>
                    <span>Retrieval score: {match.retrieval_score.toFixed(2)} · {match.suggested_status} · {match.rule_reason}</span>
                    <div className="evidence-review">
                      <button
                        type="button"
                        className="review-button"
                        onClick={() => reviewEvidenceMatch(requirement.id, match, 'accepted')}
                      >
                        {match.user_status === 'accepted' ? 'Accepted' : 'Accept evidence'}
                      </button>
                      <button
                        type="button"
                        className="review-button secondary"
                        onClick={() => reviewEvidenceMatch(requirement.id, match, 'rejected')}
                      >
                        {match.user_status === 'rejected' ? 'Rejected' : 'Reject evidence'}
                      </button>
                      {match.user_status && <span>Reviewer decision: {match.user_status}</span>}
                      <textarea
                        value={match.review_note ?? ''}
                        aria-label="Evidence review note"
                        placeholder="Add a review note"
                        onChange={(event) => {
                          const note = event.target.value
                          setMatches((current) => ({
                            ...current,
                            [requirement.id]: (current[requirement.id] ?? []).map((item) =>
                              item.id === match.id ? { ...item, review_note: note } : item,
                            ),
                          }))
                        }}
                      />
                      <button
                        type="button"
                        className="review-button secondary"
                        onClick={() => annotateEvidenceMatch(requirement.id, match)}
                      >
                        Save note
                      </button>
                    </div>
                  </div>
                ))}
              </article>
            ))}
          </div>
        </section>
      )}

      {workspaceId && (
        <section className="evidence-panel">
          <div>
            <p className="eyebrow">Evidence library</p>
            <h2>Add company evidence</h2>
            <p>Upload certificates or supporting PDFs, then retrieve candidate snippets for each requirement.</p>
          </div>
          <form onSubmit={handleEvidenceUpload}>
            <input name="evidence" type="file" accept="application/pdf,.pdf" />
            <button type="submit" disabled={evidenceBusy}>
              {evidenceBusy ? 'Uploading...' : 'Upload evidence'}
            </button>
            {evidenceStatus && <p className="upload-success">{evidenceStatus}</p>}
          </form>
        </section>
      )}

      {workspaceId && document && (
        <section className="amendment-panel">
          <div>
            <p className="eyebrow">Version review</p>
            <h2>Compare an amendment</h2>
            <p>Original tender documents remain unchanged. Changed clauses mark linked requirements for re-review.</p>
          </div>
          <form onSubmit={handleAmendmentUpload}>
            <input name="amendment" type="file" accept="application/pdf,.pdf" />
            <button type="submit" disabled={evidenceBusy}>
              {evidenceBusy ? 'Comparing...' : 'Upload and compare'}
            </button>
          </form>
          {amendment && (
            <div className="amendment-list">
              {amendmentChanges.map((change) => (
                <article className="amendment-change" key={change.id}>
                  <strong>{change.change_type} · {change.review_status}</strong>
                  {change.old_text && <p><b>Original:</b> {change.old_text} (page {change.old_page})</p>}
                  {change.new_text && <p><b>Amendment:</b> {change.new_text} (page {change.new_page})</p>}
                </article>
              ))}
            </div>
          )}
        </section>
      )}

          {workspaceId && requirements.length > 0 && (
            <section className="report-panel">
              <div className="requirements-heading">
                <div>
                  <p className="eyebrow">Decision summary</p>
                  <h2>Compliance report</h2>
                </div>
                <div className="report-actions">
                  <button type="button" className="review-button" onClick={loadReport}>Refresh summary</button>
                  <a href={getReportCsvUrl(workspaceId)} className="report-download">Download CSV</a>
                  <a href={getReportPdfUrl(workspaceId)} className="report-download">Download PDF</a>
                </div>
              </div>
              {report && (
                <>
                  <div className="report-counts">
                    <span><b>{report.compliant}</b> compliant</span>
                    <span><b>{report.needs_review}</b> needs review</span>
                    <span><b>{report.gaps}</b> gaps</span>
                    <span><b>{report.not_assessed}</b> not assessed</span>
                  </div>
                  <div className="report-rows">
                    {report.rows.map((row) => (
                      <div className="report-row" key={row.requirement_id}>
                        <span>Page {row.source_page} · {row.category}</span>
                        <strong>{row.requirement_status}</strong>
                        <p>{row.requirement_text}</p>
                        <small>{row.evidence_document ?? 'No evidence selected'} · {row.evidence_status}</small>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </section>
          )}
    </main>
  )
}

export default App
