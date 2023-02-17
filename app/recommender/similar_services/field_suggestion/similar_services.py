import logging
import time

import numpy as np
import pandas as pd
from app.exceptions import MissingStructure
from app.recommender.similar_services.preprocessor.embeddings.text_embeddings import (
    existence_text_embeddings, get_text_embeddings)
from app.settings import APP_SETTINGS
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def naive_search(fields, embeddings, embedding, similarity_threshold=None, considered_services_threshold=None):

    start_time = time.time()
    similarities = pd.DataFrame(cosine_similarity(embeddings.to_numpy(), np.array([embedding])), columns=["similarity"],
                                index=embeddings.index.to_list())
    logger.debug(f"Auto completion - Naive similarities calculation of similar services {time.time() - start_time}")

    similar_services_per_field = {}
    for field in fields:
        if similarity_threshold is None:
            similarity_threshold = APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"][field]["SIMILARITY_THRESHOLD"]

        if considered_services_threshold is None:
            considered_services_threshold = \
                APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"][field]["CONSIDERED_SERVICES_THRESHOLD"]

        # Get the most similar services
        most_similar = similarities.sort_values(by='similarity', ascending=False).head(considered_services_threshold)

        # Filter based on similarity threshold
        most_similar = most_similar[most_similar["similarity"] >= similarity_threshold]

        # Store the ids of the most similar services
        similar_services_per_field[field] = list(most_similar.index.to_list())

    return similar_services_per_field


def get_similar_services(fields, text_embedding, similarity_threshold=None, considered_services_threshold=None):
    """
    @param text_embedding: list, the text embedding of the current service
    @return: list, the similar services ids
    """

    existing_text_embeddings = get_text_embeddings()

    # Find the most similar with the current embedding
    similar_services = naive_search(fields, existing_text_embeddings, text_embedding, similarity_threshold,
                                    considered_services_threshold)

    return similar_services
