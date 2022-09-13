import logging
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from api.databases.mongo import RSMongoDB
from api.recommender.exceptions import IdNotExists, NoneServices
from api.recommender.utils import get_services

logger = logging.getLogger(__name__)


def create_similarities(create_embeddings, store_similarities):
    """
    Creates a structure with the services similarities
    @param create_embeddings: Callable, The function for creating embeddings structure
    @param store_similarities: Callable, The function for storing the created similarities
    """

    # Get all services
    db = RSMongoDB()
    resources = get_services(db)

    if resources.empty:
        raise NoneServices

    # Create embeddings
    embeddings = create_embeddings(resources)

    # Calculate similarities
    similarities_array = cosine_similarity(embeddings.to_numpy())
    indexing = resources["service_id"].to_list()
    similarities = pd.DataFrame(similarities_array, columns=indexing, index=indexing)

    # Store similarities
    store_similarities(similarities)


def update_similarities(service_id, update_embeddings, get_similarities, store_similarities):
    """
    Updates the similarities by adding a new service or editing an existing
    @param service_id: int, The id of the added or edited service
    @param update_embeddings: Callable, The function for updating the embeddings' structure
    @param get_similarities: Callable, The function for getting the current similarities
    @param store_similarities: Callable, The function for storing the calculated similarities
    """
    # Get service
    db = RSMongoDB()
    new_service = db.get_service(service_id)

    if new_service is None:
        raise IdNotExists("Service id does not exist!")

    # Update metadata structure
    embeddings = update_embeddings(new_service)

    # Get similarities structure
    similarities = get_similarities()

    # Update the metadata similarities dataframe
    service_similarities = cosine_similarity([embeddings.loc[str(service_id)].to_numpy()], embeddings.to_numpy())[0]

    # Update the <service_id> column and row
    similarities[str(service_id)] = ""
    similarities.loc[str(service_id)] = service_similarities
    similarities[str(service_id)] = service_similarities

    # Store similarities
    store_similarities(similarities)
