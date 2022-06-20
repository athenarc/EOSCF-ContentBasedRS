from pandas import read_parquet
from os import path
import pandas as pd
import logging
from sklearn.metrics.pairwise import cosine_similarity

from api.recommender.utlis import get_services
from api.settings import APP_SETTINGS
from api.database import PostgresDb

from api.recommender.embeddings.metadata_embeddings import create_metadata_embeddings

logger = logging.getLogger(__name__)


class MetadataStructure:

    def __init__(self, embeddings_path, similarities_path):

        if not path.exists(embeddings_path) or not path.exists(similarities_path):
            self.initialize_structures(embeddings_path, similarities_path)

        self.embeddings = read_parquet(embeddings_path)
        self.similarities = read_parquet(similarities_path)

    @staticmethod
    def initialize_structures(embeddings_path, similarities_path):
        logger.info("Initializing metadata structures...")

        # Get all services
        db = PostgresDb(APP_SETTINGS["CREDENTIALS"]["POSTGRES"])
        db.connect()
        resources = get_services(db)

        # Create embeddings
        embeddings = create_metadata_embeddings(resources, db)

        db.close_connection()

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
METADATA_STRUCTURES = MetadataStructure(APP_SETTINGS["EMBEDDINGS_STORAGE_PATH"] + "metadata_embeddings.parquet",
                                        APP_SETTINGS["SIMILARITIES_STORAGE_PATH"] + "metadata_similarities.parquet")
