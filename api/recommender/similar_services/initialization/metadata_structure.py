import logging
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from api.databases.mongo import RSMongoDB
from api.databases.redis import (check_key_existence, delete_object,
                                 get_object, store_object)
from api.recommender.similar_services.embeddings.metadata_embeddings import \
    create_metadata_embeddings
from api.recommender.utils import get_services
from api.recommender.exceptions import NoneServices

logger = logging.getLogger(__name__)


def create_metadata_similarities():
    logger.debug("Initializing metadata structures...")

    # Get all services
    db = RSMongoDB()
    resources = get_services(db)

    if resources.empty:
        raise NoneServices

    # Create embeddings
    embeddings = create_metadata_embeddings(resources, db)

    # Calculate similarities
    similarities_array = cosine_similarity(embeddings.to_numpy())
    indexing = resources["service_id"].to_list()
    similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)

    # Store similarities
    store_object(similarities, "METADATA_SIMILARITY")


def get_metadata_similarities():
    return get_object("METADATA_SIMILARITY")


def delete_metadata_similarities():
    delete_object("METADATA_SIMILARITY")


def existence_metadata_similarities():
    return check_key_existence("METADATA_SIMILARITY")
