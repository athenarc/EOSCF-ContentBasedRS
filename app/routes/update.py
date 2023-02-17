import logging

from app.exceptions import IdNotExists, NoneProjects, NoneServices
from app.recommender.update.updater_selector import get_updater
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/v1')


@router.get(
    "/update",
    summary="Update all data structures",
    description="The data structures created (such as embeddings) need updating every x hours.",
    tags=["update"]
)
def update():
    updater = get_updater()

    try:
        updater.update()
    except (NoneServices, NoneProjects) as e:
        logger.error("Failed to update recommenders: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update recommenders: " + str(e))


@router.get(
    "/update_for_new_service",
    summary="Updates data structures for similar services",
    tags=["update"]
)
def update_for_new_service(service_id: int):
    updater = get_updater()

    try:
        updater.update_for_new_service(service_id)
    except IdNotExists as e:
        logger.error("Failed to update similar services recommender: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update similar services recommender: " + str(e))
