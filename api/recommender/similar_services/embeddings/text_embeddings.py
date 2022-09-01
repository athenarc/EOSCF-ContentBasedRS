import pandas as pd
from api.databases.redis import (check_key_existence, delete_object,
                                 get_object, store_object)
from api.settings import APP_SETTINGS
from sentence_transformers import SentenceTransformer


def create_text_embeddings(resources):
    """
    Creates the text-based embeddings of each resource
    @param resources: DataFrame
    @return: DataFrame
    """
    sbert_settings = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SBERT"]

    # Initialize SBERT model
    model = SentenceTransformer(sbert_settings["MODEL"], device=sbert_settings["DEVICE"])

    # Get the text attributes of the resources
    text_of_resources = resources[APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"]]. \
        astype(str).apply(". ".join, axis=1)

    # Get the resources' embeddings
    sbert_embeddings = model.encode(text_of_resources.to_list())

    embeddings = pd.DataFrame(sbert_embeddings, index=resources["service_id"])
    embeddings.columns = embeddings.columns.astype(str)

    store_object(embeddings, "TEXT_EMBEDDINGS")

    return embeddings


def get_text_embeddings():
    return get_object("TEXT_EMBEDDINGS")


def delete_text_embeddings():
    delete_object("TEXT_EMBEDDINGS")


def existence_text_embeddings():
    return check_key_existence("TEXT_EMBEDDINGS")
