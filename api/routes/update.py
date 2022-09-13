import logging
from fastapi import APIRouter, HTTPException

from api.recommender.project_completion.initialization import association_rules
from api.recommender.similar_services.similarities import (
    metadata_similarities, text_similarities)
from api.recommender.exceptions import NoneServices, NoneProjects, IdNotExists

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
        metadata_similarities.create_metadata_similarities()
        text_similarities.create_text_similarities()

        # Update project completion
        association_rules.create_association_rules()

    except (NoneServices, NoneProjects) as e:
        # Delete all structures that have been initialized
        metadata_similarities.delete_metadata_similarities()
        text_similarities.delete_text_similarities()
        association_rules.delete_association_rules()

        logger.error("Failed to update recommenders: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update recommenders: " + str(e))


@router.get(
    "/update_for_new_service",
    summary="Updates data structures for similar services"
)
def update_for_new_service(service_id: int):

    try:
        metadata_similarities.update_metadata_similarities(new_service_id=service_id)
        text_similarities.update_text_similarities(new_service_id=service_id)
    except IdNotExists as e:
        logger.error("Failed to update similar services recommender: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update similar services recommender: " + str(e))
