import logging

import spacy
from app.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from app.databases.registry.registry_selector import get_registry
from app.exceptions import (DeprecatedMethod, IdNotExists, MissingAttribute,
                            MissingStructure, NoneServices)
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.sentence_filtering.service_text import \
    ServiceText
from app.settings import APP_SETTINGS
from tqdm import tqdm

logger = logging.getLogger(__name__)
sentencizer = spacy.load("en_core_web_sm")


def get_sbert_embeddings(service_text):
    """
    Calculate the embeddings per sentence of the service text.

    Args:
        service_text (ServiceText): An object of type ServiceText containing the cleaned sentences

    Returns:
        A list of embeddings of each sentence
    """
    if len(service_text.sentences) == 0:
        return []

    model = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SBERT"]["MODEL"]
    return model.encode(service_text.sentences, show_progress_bar=False)


def create_text_embeddings():
    """
    Creates the text-based embeddings of each service text
    @return: DataFrame
    """
    logger.debug("Initializing text embeddings...")
    text_attributes = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"]

    # Get all services
    db = get_registry()
    services = db.get_services(attributes=text_attributes)
    if services.empty:
        raise NoneServices

    service_texts = [ServiceText(service[APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"]])
                     for _, service in services.iterrows()]
    service_ids = services['service_id']

    # if service_texts is None:
    #     empty_text_embeddings = [(service['service_id'], []) for _, service in services.iterrows()]
    #     store_object(empty_text_embeddings, "TEXT_EMBEDDINGS")
    #     return empty_text_embeddings

    # Get the services' embeddings
    if APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]['METHOD'] == 'SBERT':
        text_embeddings = [(service_id, get_sbert_embeddings(text_service))
                           for service_id, text_service in tqdm(
                                list(zip(service_ids, service_texts)),
                                desc="Service text embeddings"
                            )]

    elif APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]['METHOD'] == 'TF-IDF':
        raise DeprecatedMethod("TF-IDF is not supported in version 3.0")
    else:
        raise ValueError("Check config. Allowed methods to generate embeddings are: \"SBERT\"")

    store_object(text_embeddings, "TEXT_EMBEDDINGS")

    return text_embeddings


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
    text_of_service = ServiceText(service_texts={attribute: service[attribute] for attribute in text_attributes})

    # Get the service's embeddings
    return get_sbert_embeddings(text_of_service)


def update_text_embedding_for_one_service(new_service_id):
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
    embeddings.append((new_service["_id"], embedding))

    return embeddings


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
