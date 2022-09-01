import logging

from api.recommender.project_completion.initialization import association_rules
from api.recommender.similar_services.initialization import (
    metadata_structure, text_structure)
from fastapi import APIRouter, HTTPException
from api.recommender.exceptions import NoneServices, NoneProjects

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
        metadata_structure.create_metadata_similarities()
        text_structure.create_text_similarities()

        # Update project completion
        association_rules.create_association_rules()

    except (NoneServices, NoneProjects) as e:
        # Delete all structures that have been initialized
        metadata_structure.delete_metadata_similarities()
        text_structure.delete_text_similarities()
        association_rules.delete_association_rules()

        logger.error("Failed to update recommenders: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update recommenders: " + str(e))
