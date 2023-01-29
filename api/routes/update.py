import logging

from api.exceptions import IdNotExists, NoneProjects, NoneServices
from api.recommender.project_completion.initialization import association_rules
from api.recommender.similar_services.preprocessor.embeddings import (
    metadata_embeddings, text_embeddings)
from api.recommender.similar_services.preprocessor.similarities import (
    metadata_similarities, text_similarities)
from api.recommender.similar_services.preprocessor.reports import monitoring_reports
from api.settings import APP_SETTINGS
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
    try:
        if APP_SETTINGS["BACKEND"]["MODE"] == "AUTO-COMPLETION":
            text_embeddings.create_text_embeddings()
        elif APP_SETTINGS["BACKEND"]["MODE"] == "RS":
            # Update similar services
            metadata_embeddings.create_metadata_embeddings()
            metadata_similarities.create_metadata_similarities()
            text_embeddings.create_text_embeddings()
            text_similarities.create_text_similarities()
            monitoring_reports.update_status_report()
            monitoring_reports.update_ar_report()

            # Update project completion
            association_rules.create_association_rules()
        elif APP_SETTINGS["BACKEND"]["MODE"] == "SIMILAR_SERVICES_EVALUATION":
            # Update similar services
            metadata_embeddings.create_metadata_embeddings()
            metadata_similarities.create_metadata_similarities()
            text_embeddings.create_text_embeddings()
            text_similarities.create_text_similarities()
            monitoring_reports.update_status_report()
            monitoring_reports.update_ar_report()
        else:
            pass  # TODO raise error

    except (NoneServices, NoneProjects) as e:
        # Delete all structures that have been initialized
        metadata_similarities.delete_metadata_similarities()
        text_similarities.delete_text_similarities()
        association_rules.delete_association_rules()
        monitoring_reports.delete_status_report()
        monitoring_reports.delete_ar_report()

        logger.error("Failed to update recommenders: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update recommenders: " + str(e))


@router.get(
    "/update_for_new_service",
    summary="Updates data structures for similar services",
    tags=["update"]
)
def update_for_new_service(service_id: int):
    try:
        if APP_SETTINGS["BACKEND"]["MODE"] == "AUTO-COMPLETION":
            text_embeddings.update_text_embedding(new_service_id=service_id)
        elif APP_SETTINGS["BACKEND"]["MODE"] == "RS":
            metadata_embeddings.update_metadata_embedding(new_service_id=service_id)
            metadata_similarities.update_metadata_similarities(new_service_id=service_id)
            text_embeddings.update_text_embedding(new_service_id=service_id)
            text_similarities.update_text_similarities(new_service_id=service_id)
            monitoring_reports.update_status_report()
            monitoring_reports.update_ar_report()
        else:
            pass  # TODO raise Exception

    except IdNotExists as e:
        logger.error("Failed to update similar services recommender: " + str(e))
        raise HTTPException(status_code=500, detail="Failed to update similar services recommender: " + str(e))
