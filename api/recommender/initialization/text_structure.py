import logging
from os import path

import pandas as pd
from api.database import PostgresDb
from api.recommender.embeddings.text_embeddings import create_text_embeddings
from api.recommender.utlis import get_services
from api.settings import APP_SETTINGS
from pandas import read_parquet
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class TextStructure:

    def __init__(self, embeddings_path, similarities_path):

        if not path.exists(embeddings_path) or not path.exists(similarities_path):
            self.initialize_structures(embeddings_path, similarities_path)

        # Load embeddings and similarities structures
        self.embeddings = read_parquet(embeddings_path)
        self.similarities = read_parquet(similarities_path)

    @staticmethod
    def initialize_structures(embeddings_path, similarities_path):
        logger.info("Initializing text structures...")

        # Get all services
        db = PostgresDb(APP_SETTINGS["CREDENTIALS"]["POSTGRES"])
        db.connect()
        resources = get_services(db)
        db.close_connection()

        # Create embeddings
        embeddings = create_text_embeddings(resources)
        # Store embeddings
        embeddings.to_parquet(embeddings_path)

        # Calculate similarities
        similarities_array = cosine_similarity(embeddings.to_numpy())
        indexing = resources["service_id"].to_list()
        similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)
        # Store similarities
        similarities.to_parquet(similarities_path)

    # getters

    # update


# global variable
TEXT_STRUCTURES = TextStructure(APP_SETTINGS["EMBEDDINGS_STORAGE_PATH"] + "text_embeddings.parquet",
                                APP_SETTINGS["SIMILARITIES_STORAGE_PATH"] + "text_similarities.parquet")
