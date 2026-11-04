from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.workspaces import router as workspaces_router
from app.api.v1.endpoints.requirements import requirement_router, router as requirements_router
from app.api.v1.endpoints.evidence import match_router as evidence_match_router
from app.api.v1.endpoints.evidence import router as evidence_router
from app.api.v1.endpoints.amendments import router as amendments_router
from app.api.v1.endpoints.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(workspaces_router)
api_router.include_router(documents_router)
api_router.include_router(requirements_router)
api_router.include_router(requirement_router)
api_router.include_router(evidence_router)
api_router.include_router(evidence_match_router)
api_router.include_router(amendments_router)
api_router.include_router(reports_router)
