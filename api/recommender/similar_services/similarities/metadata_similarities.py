import logging

from api.databases.redis import (check_key_existence, delete_object,
                                 get_object, store_object)
from api.recommender.similar_services.embeddings.metadata_embeddings import \
    create_metadata_embeddings
from api.recommender.similar_services.embeddings.metadata_embeddings import update_metadata_embedding
from api.recommender.similar_services.similarities.similarities import update_similarities, create_similarities

logger = logging.getLogger(__name__)


def create_metadata_similarities():
    logger.debug("Initializing metadata structures...")
    create_similarities(create_metadata_embeddings, store_metadata_similarities)


def update_metadata_similarities(new_service_id):
    """
    Updates the metadata by adding a new service or editing an existing
    """
    logger.debug("Update metadata similarities for addition/update of a service...")
    update_similarities(new_service_id, update_metadata_embedding, get_metadata_similarities,
                        store_metadata_similarities)


def get_metadata_similarities():
    return get_object("METADATA_SIMILARITY")


def store_metadata_similarities(similarities):
    return store_object(similarities, "METADATA_SIMILARITY")


def delete_metadata_similarities():
    delete_object("METADATA_SIMILARITY")


def existence_metadata_similarities():
    return check_key_existence("METADATA_SIMILARITY")
