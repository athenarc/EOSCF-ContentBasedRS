import logging

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def create_similarities(get_embeddings, store_similarities):
    """
    Creates a structure with the services similarities
    @param get_embeddings: Callable, The function for getting the embeddings structure
    @param store_similarities: Callable, The function for storing the created similarities
    """

    # Get embeddings
    embeddings = get_embeddings()

    # Calculate similarities
    similarities_array = cosine_similarity(embeddings.to_numpy())
    indexing = embeddings.index
    similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)
    # Store similarities
    store_similarities(similarities)


def update_similarities(service_id, get_embeddings, get_similarities, store_similarities):
    """
    Updates the similarities by adding a new service or editing an existing
    @param service_id: int, The id of the added or edited service
    @param get_embeddings: Callable, The function for getting the embeddings' structure
    @param get_similarities: Callable, The function for getting the current similarities
    @param store_similarities: Callable, The function for storing the calculated similarities
    """

    # Get embeddings structure
    embeddings = get_embeddings()

    # Get similarities structure
    similarities = get_similarities()

    # Update the metadata similarities dataframe
    service_similarities = cosine_similarity([embeddings.loc[service_id].to_numpy()], embeddings.to_numpy())[0]

    # Update the <service_id> column and row
    similarities[service_id] = 0
    similarities.loc[service_id] = service_similarities
    similarities[service_id] = service_similarities

    # Store similarities
    store_similarities(similarities)


def initialize_similarities(existence_similarities, get_embeddings, store_similarities, init_msg):
    """
    @param existence_similarities:
    @param get_embeddings: Callable, The function for getting the embeddings' structure
    @param store_similarities: Callable, The function for storing the calculated similarities
    @param init_msg: str, log message
    @return:
    """
    if not existence_similarities():
        logging.info(init_msg)
        create_similarities(get_embeddings, store_similarities)
