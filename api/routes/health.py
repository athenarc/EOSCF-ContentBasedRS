import logging

from api.health.monitor_health import service_health_test
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/v1')


@router.get(
    "/health",
    summary="Make sure that all components are working",
    tags=["health"]
)
def service_health():
    return service_health_test()
