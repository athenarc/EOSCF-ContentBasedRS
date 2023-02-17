import logging

import pandas as pd
from app.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from app.databases.registry.registry_selector import get_registry
from app.exceptions import (IdNotExists, MissingAttribute, MissingStructure,
                            NoneServices)
from app.settings import APP_SETTINGS
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


def generate_sbert_embedding(text):
    model = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SBERT"]["MODEL"]
    sbert_embedding = model.encode([text],
                                   show_progress_bar=False if APP_SETTINGS['BACKEND']['PROD'] else False)
    return sbert_embedding[0]


def create_text_embedding(service):
    """
    CARE: We do not cover the case of a single update for the TF-IDF method
    """
    text_attributes = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"]
    service_attributes = list(service.keys())

    # Check that all the necessary fields exist in the service
    if not all(text_attribute in service_attributes for text_attribute in text_attributes):
        raise MissingAttribute("Resource does not have all necessary fields! Make sure that "
                               f"{text_attributes} are given!")

    # Get the text attributes of the service
    text_of_service = ". ".join([
        service[attribute] for attribute in text_attributes])

    # Get the service's embeddings
    return generate_sbert_embedding(text_of_service)


def update_text_embedding(new_service_id):
    # Get service
    db = get_registry()
    new_service = db.get_service(new_service_id)

    if new_service is None:
        raise IdNotExists("Service id does not exist!")

    # Create the embedding of the new service
    embedding = create_text_embedding(new_service)

    # Get embeddings
    embeddings = get_text_embeddings()

    # Update
    embeddings.loc[new_service["_id"]] = embedding

    return embeddings


def get_sbert_embeddings(text_of_services):
    model = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SBERT"]["MODEL"]
    return model.encode(text_of_services.to_list())


def get_tf_idf_embeddings(text_of_services):
    tf_idf_vectorizer = TfidfVectorizer()
    vectorized = tf_idf_vectorizer.fit_transform(text_of_services)

    svd = TruncatedSVD(n_components=300)  # The same number as the SBERT embeddings
    return svd.fit_transform(vectorized)


def create_text_embeddings():
    """
    Creates the text-based embeddings of each service
    @return: DataFrame
    """
    logger.debug("Initializing text embeddings...")

    # Get all services
    db = get_registry()
    services = db.get_services(attributes=APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"] +
                                          APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA"])

    if services.empty:
        raise NoneServices

    def concatenate_row(row):
        return ". ".join(row.transform(lambda attr: ", ".join(attr) if type(attr) is list else attr))

    # Get the text attributes of the services
    text_of_services = services[APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"]].apply(concatenate_row, axis=1)

    # Get the services' embeddings
    if APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]['METHOD'] == 'SBERT':
        text_embeddings = get_sbert_embeddings(text_of_services)
    elif APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]['METHOD'] == 'TF-IDF':
        text_embeddings = get_tf_idf_embeddings(text_of_services)
    else:
        raise ValueError("Check config. Allowed methods to generate embeddings are: \"TF-IDF\" or \"SBERT\"")

    embeddings_df = pd.DataFrame(text_embeddings, index=services["service_id"])
    store_object(embeddings_df, "TEXT_EMBEDDINGS")

    return embeddings_df


def existence_text_embeddings():
    return check_key_existence("TEXT_EMBEDDINGS")


def get_text_embeddings():
    if not existence_text_embeddings():
        raise MissingStructure("Text embeddings do not exist!")
    return get_object("TEXT_EMBEDDINGS")


def delete_text_embeddings():
    delete_object("TEXT_EMBEDDINGS")


def initialize_text_embeddings():
    if not existence_text_embeddings():
        logging.info("Text embeddings do not exist.Creating...")
        create_text_embeddings()
