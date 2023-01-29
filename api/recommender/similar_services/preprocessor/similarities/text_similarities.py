import logging

from api.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from api.exceptions import MissingStructure
from api.recommender.similar_services.preprocessor.embeddings.text_embeddings import (
    get_text_embeddings)
from api.recommender.similar_services.preprocessor.similarities.similarities import (
    create_similarities, update_similarities, initialize_similarities)

logger = logging.getLogger(__name__)


def create_text_similarities():
    logger.debug("Initializing text similarities...")

    create_similarities(get_text_embeddings, store_text_similarities)


def update_text_similarities(new_service_id):
    """
    Updates the text structures by adding a new service or editing an existing
    """
    logger.debug("Update text structures for addition/update of a service...")
    update_similarities(new_service_id, get_text_embeddings, get_text_similarities,
                        store_text_similarities)


def existence_text_similarities():
    return check_key_existence("TEXT_SIMILARITY")


def get_text_similarities():
    if not existence_text_similarities():
        raise MissingStructure("Text similarities do not exist!")
    return get_object("TEXT_SIMILARITY")


def store_text_similarities(similarities):
    return store_object(similarities, "TEXT_SIMILARITY")


def delete_text_similarities():
    delete_object("TEXT_SIMILARITY")


def initialize_text_similarities():
    initialize_similarities(existence_text_similarities, get_text_embeddings, store_text_similarities,
                            init_msg="Text similarities do not exist.Creating...")
