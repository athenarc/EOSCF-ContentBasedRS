import logging

import numpy as np
import pandas as pd
from app.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from app.exceptions import MissingStructure
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings.text_embeddings import \
    get_text_embeddings
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.similarities.similarity_abc import \
    SimilaritiesManager
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

logger = logging.getLogger(__name__)


class TextSimilaritiesManager(SimilaritiesManager):
    def create_similarities(self):
        logger.debug("Initializing text similarities...")

        embeddings = get_text_embeddings()

        # Check if text embeddings exist
        if len(embeddings[0][1]) > 0:
            similarities_array = [
                self.calculate_similarities_of_service(service_embeddings, embeddings)
                for _, service_embeddings in tqdm(embeddings, desc="Pairwise text similarities")
            ]
            service_ids = [service_id for service_id, _ in embeddings]

            similarities = pd.DataFrame(similarities_array, columns=service_ids, index=service_ids)
        else:
            indexing = [service_id for service_id, _ in embeddings]
            similarities = pd.DataFrame(0, columns=indexing, index=indexing)

        # Store similarities
        self.store_similarities(similarities)

    @staticmethod
    def calculate_sdr_similarity(service_embeddings_a, service_embeddings_b):
        pairwise_similarities = cosine_similarity(service_embeddings_a, service_embeddings_b)
        return np.average(np.max(pairwise_similarities, axis=1))

    def calculate_similarities_of_service(self, service_embeddings, all_services_embeddings):
        return [self.calculate_sdr_similarity(service_embeddings, other_service_embedding)
                for _, other_service_embedding in all_services_embeddings]

    def update_similarities_for_one_service(self, new_service_id):
        """
        Updates the text structures by adding a new service or editing an existing
        """
        logger.debug("Update text structures for addition/update of a service...")

        # Get embeddings structure
        embeddings = get_text_embeddings()
        # Get similarities structure
        similarities = self.get_similarities()

        if len(embeddings) > 0:
            def find_ind(service_id):
                """This is error-prone, bad practise, and super slow.
                Will be fixed when the embeddings structure is updated """
                ind = 0
                for service_id_in_list, _ in embeddings:
                    if service_id == service_id_in_list:
                        return ind
                    ind += 1

            # Update the metadata similarities dataframe
            service_similarities = self.calculate_similarities_of_service(
                embeddings[find_ind(new_service_id)][1],
                embeddings
            )
        else:
            service_similarities = pd.Series(0, index=similarities.index)

        similarities[new_service_id] = 0
        similarities.loc[new_service_id] = service_similarities
        similarities[new_service_id] = service_similarities

        # Store similarities
        self.store_similarities(similarities)

    def initialize_similarities(self):
        if not self.existence_similarities():
            logging.info("Text similarities do not exist.Creating...")
            self.create_similarities()

    @staticmethod
    def existence_similarities():
        return check_key_existence("TEXT_SIMILARITY")

    def get_similarities(self):
        if not self.existence_similarities():
            raise MissingStructure("Text similarities do not exist!")
        return get_object("TEXT_SIMILARITY")

    @staticmethod
    def store_similarities(similarities):
        return store_object(similarities, "TEXT_SIMILARITY")

    @staticmethod
    def delete_similarities():
        delete_object("TEXT_SIMILARITY")
