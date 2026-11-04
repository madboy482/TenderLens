export type HealthResponse = {
  status: string
  service: string
  environment: string
}

export type Workspace = {
  id: string
  title: string
  tender_reference: string | null
  organization_label: string | null
  created_at: string
  updated_at: string
}

export type Document = {
  id: string
  workspace_id: string
  original_name: string
  page_count: number
  processing_status: string
  warnings: string[]
}

export type DocumentChunk = {
  id: string
  page_start: number
  page_end: number
  chunk_text: string
  chunk_type: string
}

export type DocumentDetail = Document & {
  pages: {
    id: string
    page_number: number
    extracted_text: string
    extraction_status: string
  }[]
  chunks: DocumentChunk[]
}

export type Requirement = {
  id: string
  source_page_start: number
  source_page_end: number | null
  source_clause_text: string
  normalized_text: string
  category: string
  requirement_type: string
  mandatory_status: string
  extracted_value: string | null
  normalized_value: string | null
  unit: string | null
  confidence: number | null
  review_required: boolean
  suggested_status: string
  confirmed_status: string | null
  review_note: string | null
}

export type EvidenceMatch = {
  id: string
  requirement_id: string
  evidence_document_id: string
  evidence_chunk_id: string
  retrieval_score: number
  matched_terms: string | null
  suggested_status: string
  rule_reason: string | null
  user_status: string | null
  review_note: string | null
  evidence_document_name: string
  evidence_page_start: number
  evidence_snippet: string
}

export type AmendmentChange = {
  id: string
  original_document_id: string
  amendment_document_id: string
  old_text: string | null
  new_text: string | null
  old_page: number | null
  new_page: number | null
  change_type: string
  review_status: string
  affected_requirement_ids: string | null
}

export type ComplianceSummary = {
  workspace_id: string
  workspace_title: string
  total_requirements: number
  compliant: number
  needs_review: number
  gaps: number
  not_assessed: number
  rows: {
    requirement_id: string
    source_page: number
    category: string
    requirement_text: string
    mandatory_status: string
    requirement_status: string
    evidence_status: string
    evidence_document: string | null
    evidence_page: number | null
    rule_reason: string | null
    review_required: boolean
    review_note: string | null
  }[]
}

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL
const localApiBaseUrl =
  typeof window !== 'undefined'
    ? `http://${window.location.hostname}:8000/api/v1`
    : 'http://localhost:8000/api/v1'
const apiBaseUrl = configuredApiBaseUrl ?? localApiBaseUrl

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/health`)

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`)
  }

  return response.json() as Promise<HealthResponse>
}

export async function createWorkspace(title: string): Promise<Workspace> {
  const response = await fetch(`${apiBaseUrl}/workspaces`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
  if (!response.ok) throw new Error('Could not create workspace')
  return response.json() as Promise<Workspace>
}

export async function uploadTender(workspaceId: string, file: File): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${apiBaseUrl}/workspaces/${workspaceId}/documents`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new Error(error?.detail ?? 'Could not upload tender')
  }
  return response.json() as Promise<Document>
}

export async function getDocument(documentId: string): Promise<DocumentDetail> {
  const response = await fetch(`${apiBaseUrl}/documents/${documentId}`)
  if (!response.ok) throw new Error('Could not load extracted document')
  return response.json() as Promise<DocumentDetail>
}

export async function getRequirements(workspaceId: string): Promise<Requirement[]> {
  const response = await fetch(`${apiBaseUrl}/workspaces/${workspaceId}/requirements`)
  if (!response.ok) throw new Error('Could not load requirements')
  return response.json() as Promise<Requirement[]>
}

export async function updateRequirement(
  requirementId: string,
  changes: Partial<Pick<Requirement, 'normalized_text' | 'category' | 'mandatory_status' | 'confirmed_status' | 'review_note'>>,
): Promise<Requirement> {
  const response = await fetch(`${apiBaseUrl}/requirements/${requirementId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(changes),
  })
  if (!response.ok) throw new Error('Could not save requirement review')
  return response.json() as Promise<Requirement>
}

export async function uploadEvidence(workspaceId: string, file: File): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${apiBaseUrl}/workspaces/${workspaceId}/evidence`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error('Could not upload evidence')
  return response.json() as Promise<Document>
}

export async function matchEvidence(requirementId: string): Promise<EvidenceMatch[]> {
  const response = await fetch(`${apiBaseUrl}/requirements/${requirementId}/match-evidence`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Could not retrieve evidence matches')
  return response.json() as Promise<EvidenceMatch[]>
}

export async function updateEvidenceMatch(
  matchId: string,
  changes: Pick<EvidenceMatch, 'user_status' | 'review_note'>,
): Promise<EvidenceMatch> {
  const response = await fetch(`${apiBaseUrl}/evidence-matches/${matchId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(changes),
  })
  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new Error(error?.detail ?? 'Could not save evidence review')
  }
  return response.json() as Promise<EvidenceMatch>
}

export async function uploadAmendment(workspaceId: string, file: File): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${apiBaseUrl}/workspaces/${workspaceId}/amendments`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error('Could not upload amendment')
  return response.json() as Promise<Document>
}

export async function compareAmendment(
  workspaceId: string,
  originalDocumentId: string,
  amendmentDocumentId: string,
): Promise<AmendmentChange[]> {
  const query = new URLSearchParams({
    original_document_id: originalDocumentId,
    amendment_document_id: amendmentDocumentId,
  })
  const response = await fetch(`${apiBaseUrl}/workspaces/${workspaceId}/compare-amendment?${query}`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Could not compare amendment')
  return response.json() as Promise<AmendmentChange[]>
}

export async function getReport(workspaceId: string): Promise<ComplianceSummary> {
  const response = await fetch(`${apiBaseUrl}/workspaces/${workspaceId}/report`)
  if (!response.ok) throw new Error('Could not load compliance report')
  return response.json() as Promise<ComplianceSummary>
}

export function getReportCsvUrl(workspaceId: string): string {
  return `${apiBaseUrl}/workspaces/${workspaceId}/report.csv`
}

export function getReportPdfUrl(workspaceId: string): string {
  return `${apiBaseUrl}/workspaces/${workspaceId}/report.pdf`
}
