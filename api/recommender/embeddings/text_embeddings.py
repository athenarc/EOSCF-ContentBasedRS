import pandas as pd
from sentence_transformers import SentenceTransformer

from api.settings import APP_SETTINGS


def create_text_embeddings(resources):
    """
    Creates the text-based embeddings of each resource
    @param resources: DataFrame
    @return: DataFrame
    """
    # Initialize SBERT model
    model = SentenceTransformer(APP_SETTINGS["SBERT"]["MODEL"], device=APP_SETTINGS["SBERT"]["DEVICE"])

    # Get the text attributes of the resources
    text_of_resources = resources["name"] + ". " + resources["description"]

    # Get the resources' embeddings
    SBERT_embeddings = model.encode(text_of_resources.to_list())

    embeddings = pd.DataFrame(SBERT_embeddings, index=resources["service_id"])
    embeddings.columns = embeddings.columns.astype(str)

    return embeddings
