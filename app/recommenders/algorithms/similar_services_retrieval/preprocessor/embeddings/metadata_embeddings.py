import logging

import numpy as np
import pandas as pd
from app.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from app.databases.registry.registry_selector import get_registry
from app.exceptions import IdNotExists, MissingStructure, NoneServices
from app.settings import APP_SETTINGS
from sklearn.preprocessing import MultiLabelBinarizer

logger = logging.getLogger(__name__)


def create_metadata_embedding(service):
    # Get the binarizers
    if not existence_metadata_binarizers():
        raise MissingStructure("Binarizers cannot be found!")

    binarizers = get_metadata_binarizers()

    # Calculate the embedding of the service
    partial_embedding = []
    for attribute, binarizer in binarizers.items():
        partial_embedding.append(binarizer.transform([service[attribute]]))

    if len(partial_embedding):
        embedding = np.concatenate(tuple(partial_embedding), axis=1)
        return embedding[0]
    else:
        return np.empty([0])


def update_metadata_embedding_for_one_service(new_service_id):
    # Get service
    db = get_registry()
    new_service = db.get_service(new_service_id)

    if new_service is None:
        raise IdNotExists("Service id does not exist!")

    # Create the embedding of the new service
    embedding = create_metadata_embedding(new_service)

    # Get embeddings
    embeddings = get_metadata_embeddings()

    # Update
    embeddings.loc[new_service["_id"]] = embedding

    return embeddings


def create_metadata_embeddings():
    """
    Creates the metadata-based embeddings of each service
    @return: Dataframe
    """
    logger.debug("Initializing metadata embeddings...")

    metadata = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]['METADATA']

    # Get all services
    db = get_registry()
    services = db.get_services(attributes=metadata)

    if services.empty:
        raise NoneServices

    # Create new binarizers
    partial_embeddings = []
    binarizers = {}

    # e.g., attribute = scientific_domains
    for attribute in metadata:
        # Initialize binarizers
        binarizers[attribute] = MultiLabelBinarizer(classes=getattr(db, "get_" + attribute)())
        # Transform services attribute to one-hot encoding
        partial_embeddings.append(binarizers[attribute].fit_transform(services[attribute]))

    # save the binarizers
    store_object(binarizers, "METADATA_BINARIZERS")

    # Concatenate the embeddings of all attributes
    embeddings = pd.DataFrame(data=np.concatenate(tuple(partial_embeddings), axis=1) if len(partial_embeddings) else [],
                              index=services["service_id"].to_list())

    store_object(embeddings, "METADATA_EMBEDDINGS")

    return embeddings


def get_metadata_binarizers():
    return get_object("METADATA_BINARIZERS")


def delete_metadata_binarizer():
    delete_object("METADATA_BINARIZERS")


def existence_metadata_binarizers():
    return check_key_existence("METADATA_BINARIZERS")


def existence_metadata_embeddings():
    return check_key_existence("METADATA_EMBEDDINGS")


def get_metadata_embeddings():
    if not existence_metadata_embeddings():
        raise MissingStructure("Metadata embeddings do not exist!")
    return get_object("METADATA_EMBEDDINGS")


def delete_metadata_embeddings():
    delete_object("METADATA_EMBEDDINGS")


def initialize_metadata_embeddings():
    if not existence_metadata_embeddings():
        logging.info("Metadata embeddings do not exist.Creating...")
        create_metadata_embeddings()
