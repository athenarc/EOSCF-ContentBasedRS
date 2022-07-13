import logging

from api.recommender.similar_services.initialization.metadata_structure import \
    METADATA_STRUCTURES
from api.recommender.similar_services.initialization.text_structure import \
    TEXT_STRUCTURES
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/update",
    summary="Update all data structures",
    description="The data structures created (such as embeddings) need updating every x hours."
)
def update():
    try:
        # Update similar services
        TEXT_STRUCTURES.update()
        METADATA_STRUCTURES.update()
        # Update project completion
    except Exception as e:
        # Delete all structures that have been initialized
        TEXT_STRUCTURES.delete()
        METADATA_STRUCTURES.delete()

        logger.error("Failed to update recommenders: " + str(e))
        raise HTTPException(status_code=404, detail="Failed to update recommenders: " + str(e))
