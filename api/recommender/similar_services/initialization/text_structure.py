import logging
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from api.databases.mongo import RSMongoDB
from api.databases.redis import (check_key_existence, delete_object,
                                 get_object, store_object)
from api.recommender.similar_services.embeddings.text_embeddings import \
    create_text_embeddings
from api.recommender.utils import get_services
from api.recommender.exceptions import NoneServices

logger = logging.getLogger(__name__)


def create_text_similarities():
    logger.debug("Initializing text structures...")

    # Get all services
    db = RSMongoDB()
    resources = get_services(db)

    if resources.empty:
        raise NoneServices

    # Create embeddings
    embeddings = create_text_embeddings(resources)

    # Calculate similarities
    similarities_array = cosine_similarity(embeddings.to_numpy())
    indexing = resources["service_id"].to_list()
    similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)

    # Store similarities
    store_object(similarities, "TEXT_SIMILARITY")


def get_text_similarities():
    return get_object("TEXT_SIMILARITY")


def delete_text_similarities():
    delete_object("TEXT_SIMILARITY")


def existence_text_similarities():
    return check_key_existence("TEXT_SIMILARITY")
