from fastapi import APIRouter

from app.api.health.schemas import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["Health"],
    responses={503: {"description": "Service unavailable"}},
)


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns service alive status",
)
async def health_check():
    return HealthResponse()
