import logging

import pandas as pd
from app.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from app.exceptions import MissingStructure
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings.metadata_embeddings import \
    get_metadata_embeddings
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.similarities.similarity_abc import \
    SimilaritiesManager
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class MetadataSimilaritiesManager(SimilaritiesManager):
    def create_similarities(self):
        logger.debug("Initializing metadata similarities...")

        embeddings = get_metadata_embeddings()
        indexing = embeddings.index

        if not embeddings.empty:
            # Calculate similarities
            similarities_array = cosine_similarity(embeddings.to_numpy())
            similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)
        else:  # If the dimension of the embeddings is zero (there are no attributes considered)
            similarities = pd.DataFrame(0, columns=indexing, index=indexing)

        # Store similarities
        self.store_similarities(similarities)

    def update_similarities_for_one_service(self, new_service_id):
        """
        Updates the metadata by adding a new service or editing an existing
        """
        logger.debug("Update metadata similarities for addition/update of a service...")

        # Get embeddings structure
        embeddings = get_metadata_embeddings()
        # Get similarities structure
        similarities = self.get_similarities()

        if not embeddings.empty:
            # Update the metadata similarities dataframe
            service_similarities = cosine_similarity([embeddings.loc[new_service_id].to_numpy()],
                                                     embeddings.to_numpy())[0]
        else:
            service_similarities = pd.Series(0, index=similarities.index)

        # Update the <service_id> column and row
        similarities[new_service_id] = 0
        similarities.loc[new_service_id] = service_similarities
        similarities[new_service_id] = service_similarities

        # Store similarities
        self.store_similarities(similarities)

    def initialize_similarities(self):
        if not self.existence_similarities():
            logging.info("Metadata similarities do not exist.Creating...")
            self.create_similarities()

    @staticmethod
    def existence_similarities():
        return check_key_existence("METADATA_SIMILARITY")

    def get_similarities(self):
        if not self.existence_similarities():
            raise MissingStructure("Text similarities do not exist!")
        return get_object("METADATA_SIMILARITY")

    @staticmethod
    def store_similarities(similarities):
        return store_object(similarities, "METADATA_SIMILARITY")

    @staticmethod
    def delete_similarities():
        delete_object("METADATA_SIMILARITY")
