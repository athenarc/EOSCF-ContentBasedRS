import logging

from api.recommender.initialization.metadata_structure import METADATA_STRUCTURES
from api.recommender.initialization.text_structure import TEXT_STRUCTURES
from api.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


def populate_structures():
    logger.info("Populate structures...")

    METADATA_STRUCTURES.initialize_structures(APP_SETTINGS["EMBEDDINGS_STORAGE_PATH"] + "metadata_embeddings.parquet",
                                              APP_SETTINGS["SIMILARITIES_STORAGE_PATH"] + "metadata_similarities.parquet")
    TEXT_STRUCTURES.initialize_structures(APP_SETTINGS["EMBEDDINGS_STORAGE_PATH"] + "text_embeddings.parquet",
                                          APP_SETTINGS["SIMILARITIES_STORAGE_PATH"] + "text_similarities.parquet")

