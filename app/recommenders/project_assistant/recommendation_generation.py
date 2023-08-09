import pandas as pd
from app.databases.registry.registry_selector import get_registry
from app.exceptions import NoTextAttributes
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.embeddings.text_embeddings import (
    ServiceText, get_sbert_embeddings, get_text_embeddings)
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.similarities.text_similarities import \
    TextSimilaritiesManager
from app.settings import APP_SETTINGS


def filter_by_status(db, services):
    # Get non-published services
    non_published_services = db.get_non_published_services(list(services.index))

    # Get the indexes of viewing, purchased and non-published services
    indexes_to_drop = list(non_published_services)

    return services.drop(index=indexes_to_drop)


def get_similar_services(description_embedding):
    if len(APP_SETTINGS['BACKEND']['SIMILAR_SERVICES']['TEXT_ATTRIBUTES']) == 0:
        raise NoTextAttributes(f"FATAL: Project assistant cannot run with empty attributes in the config.")

    existing_text_embeddings = get_text_embeddings()

    similarity_with_services = TextSimilaritiesManager().calculate_similarities_of_service(
        description_embedding, existing_text_embeddings
    )
    similarity_with_services_df = pd.DataFrame(
        similarity_with_services, columns=["similarity"],
        index=[ind for ind, _ in existing_text_embeddings]
    )

    similarity_threshold = APP_SETTINGS["BACKEND"]["PROJECT_ASSISTANT"]["SIMILARITY_THRESHOLD"]

    similar_services = similarity_with_services_df[similarity_with_services_df["similarity"] >= similarity_threshold]

    return similar_services


def project_assistant_recommendation(prompt, max_num):
    """
    Returns a list of recommended services and their score
    Args:
        prompt: str, The prompt provided for the new service of the project
        max_num: int, The maximum number of recommendations we want returned
    """

    # Calculate the text embeddings per sentence of the given description
    description_embedding = get_sbert_embeddings(ServiceText(service_texts={"prompt": prompt}))

    # Get similar services ids
    similar_services = get_similar_services(description_embedding)

    # Filter similar services based on status
    db = get_registry()
    similar_services = filter_by_status(db, similar_services)

    # Order similar services
    similar_services = similar_services.sort_values(by=["similarity"], ascending=False)

    return [{"service_id": service_id, "score": score["similarity"]} for service_id, score in
            similar_services[:max_num].iterrows()]
