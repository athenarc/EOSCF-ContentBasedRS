import logging

from api.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from api.exceptions import MissingStructure
from api.recommender.similar_services.preprocessor.embeddings.metadata_embeddings import get_metadata_embeddings
from api.recommender.similar_services.preprocessor.similarities.similarities import (
    create_similarities, update_similarities, initialize_similarities)

logger = logging.getLogger(__name__)


def create_metadata_similarities():
    logger.debug("Initializing metadata similarities...")
    create_similarities(get_metadata_embeddings, store_metadata_similarities)


def update_metadata_similarities(new_service_id):
    """
    Updates the metadata by adding a new service or editing an existing
    """
    logger.debug("Update metadata similarities for addition/update of a service...")
    update_similarities(new_service_id, get_metadata_embeddings, get_metadata_similarities,
                        store_metadata_similarities)


def existence_metadata_similarities():
    return check_key_existence("METADATA_SIMILARITY")


def get_metadata_similarities():
    if not existence_metadata_similarities():
        raise MissingStructure("Text similarities do not exist!")
    return get_object("METADATA_SIMILARITY")


def store_metadata_similarities(similarities):
    return store_object(similarities, "METADATA_SIMILARITY")


def delete_metadata_similarities():
    delete_object("METADATA_SIMILARITY")


def initialize_metadata_similarities():
    initialize_similarities(existence_metadata_similarities, get_metadata_embeddings, store_metadata_similarities,
                            init_msg="Metadata similarities do not exist.Creating...")
