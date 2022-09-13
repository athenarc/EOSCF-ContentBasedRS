import logging

from api.databases.redis import (check_key_existence, delete_object,
                                 get_object, store_object)
from api.recommender.similar_services.embeddings.text_embeddings import \
    create_text_embeddings
from api.recommender.similar_services.similarities.similarities import update_similarities, create_similarities
from api.recommender.similar_services.embeddings.text_embeddings import update_text_embedding

logger = logging.getLogger(__name__)


def create_text_similarities():
    logger.debug("Initializing text structures...")
    create_similarities(create_text_embeddings, store_text_similarities)


def update_text_similarities(new_service_id):
    """
    Updates the text structures by adding a new service or editing an existing
    """
    logger.debug("Update text structures for addition/update of a service...")
    update_similarities(new_service_id, update_text_embedding, get_text_similarities,
                        store_text_similarities)


def get_text_similarities():
    return get_object("TEXT_SIMILARITY")


def store_text_similarities(similarities):
    return store_object(similarities, "TEXT_SIMILARITY")


def delete_text_similarities():
    delete_object("TEXT_SIMILARITY")


def existence_text_similarities():
    return check_key_existence("TEXT_SIMILARITY")
