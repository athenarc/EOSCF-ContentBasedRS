import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from api.databases.registry.registry_selector import get_registry
from api.settings import APP_SETTINGS
from api.recommender.similar_services.preprocessor.embeddings.text_embeddings import \
    get_text_embeddings, generate_sbert_embedding

def filter_by_status(db, services):
    # Get non-published resources
    non_published_resources = db.get_non_published_services(list(services.index))

    # Get the indexes of viewing, purchased and non-published resources
    indexes_to_drop = list(non_published_resources)

    return services.drop(index=indexes_to_drop)


def get_similar_services(description_embedding):

    existing_text_embeddings = get_text_embeddings()

    similar_services = pd.DataFrame(cosine_similarity(existing_text_embeddings.to_numpy(), np.array([description_embedding])), columns=["similarity"],
                                index=existing_text_embeddings.index.to_list())


    similarity_threshold = APP_SETTINGS["BACKEND"]["PROJECT_ASSISTANT"]["SIMILARITY_THRESHOLD"]

    similar_services = similar_services[similar_services["similarity"] >= similarity_threshold]

    return similar_services

def project_assistant_recommendation(description, max_num):
    """
    Returns a list of recommended services and their score
    Args:
        description: str, The description provided for the new service of the project
        max_num: int, The maximum number of recommendations we want returned
    """

    # Calculate the text embedding of the given description
    description_embedding = generate_sbert_embedding(description)

    # Get similar services ids
    similar_services = get_similar_services(description_embedding)

    # Filter similar services based on status
    db = get_registry()
    similar_services = filter_by_status(db, similar_services)

    # Order similar services
    similar_services = similar_services.sort_values(by=["similarity"], ascending=False)

    return [{"service_id": service_id, "score": score["similarity"]} for service_id, score in
                      similar_services[:max_num].iterrows()]