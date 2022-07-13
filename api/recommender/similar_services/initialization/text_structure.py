import logging
from os import path
from pandas import read_parquet
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from api.databases.mongo import RSMongoDB
from api.recommender.similar_services.embeddings.text_embeddings import \
    create_text_embeddings
from api.recommender.utils import get_services, silent_remove
from api.settings import APP_SETTINGS


logger = logging.getLogger(__name__)


class TextStructure:

    def __init__(self, embeddings_path, similarities_path):

        self._embeddings_path = embeddings_path
        self._similarities_path = similarities_path

        try:
            if not path.exists(self._embeddings_path) or not path.exists(self._similarities_path):
                self.initialize_structures()

            # Load embeddings and similarities structures
            self._embeddings = read_parquet(self._embeddings_path)
            self._similarities = read_parquet(self._similarities_path)
        except Exception as e:
            logger.error("Error in text structure initialization: " + str(e))
            self._embeddings = None
            self._similarities = None

    def initialize_structures(self):
        logger.info("Initializing text structures...")

        # Get all services
        db = RSMongoDB()
        resources = get_services(db)

        # Create embeddings
        embeddings = create_text_embeddings(resources)
        # Store embeddings
        embeddings.to_parquet(self._embeddings_path)

        # Calculate similarities
        similarities_array = cosine_similarity(embeddings.to_numpy())
        indexing = resources["service_id"].to_list()
        similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)
        # Store similarities
        similarities.to_parquet(self._similarities_path)

    def embeddings(self):
        # TODO if not initialized embeddings?
        return self._embeddings

    def similarities(self):
        # TODO if not initialized similarities?
        return self._similarities

    def update(self):

        self.delete()

        self.initialize_structures()
        self._embeddings = read_parquet(self._embeddings_path)
        self._similarities = read_parquet(self._similarities_path)

    def delete(self):
        silent_remove(self._embeddings_path)
        self._embeddings = None
        silent_remove(self._similarities_path)
        self._similarities = None


# global variable
TEXT_STRUCTURES = TextStructure(APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["EMBEDDINGS_STORAGE_PATH"] + "text_embeddings.parquet",
                                APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SIMILARITIES_STORAGE_PATH"] + "text_similarities.parquet")
