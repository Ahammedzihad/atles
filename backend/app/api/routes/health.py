from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return health status of the Atles backend service."""
    return HealthResponse(status="ok", service=settings.SERVICE_NAME)
