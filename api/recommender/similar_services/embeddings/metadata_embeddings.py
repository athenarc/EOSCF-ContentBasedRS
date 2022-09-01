import os
from pickle import dump
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

from api.settings import APP_SETTINGS
from api.databases.redis import (check_key_existence, delete_object,
                                 get_object, store_object)


def create_metadata_embeddings(resources, db):
    """
    Creates the metadata-based embeddings of each resource
    @param resources:
    @param db: PostgresDB
    @return: Dataframe
    """

    # Create new binarizers
    partial_embeddings = []
    binarizers = {}

    # e.g., attribute = scientific_domains
    for attribute in APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]['METADATA']:
        # Initialize binarizers
        binarizers[attribute] = MultiLabelBinarizer(classes=getattr(db, "get_"+attribute)())
        # Transform resources attribute to one-hot encoding
        partial_embeddings.append(binarizers[attribute].fit_transform(resources[attribute]))

    # save the binarizers
    store_object(binarizers, "METADATA_BINARIZERS")

    # Concatenate the embeddings of all attributes
    embeddings = pd.DataFrame(data=np.concatenate(tuple(partial_embeddings), axis=1),
                              index=resources["service_id"].to_list())
    embeddings.columns = embeddings.columns.astype(str)

    store_object(embeddings, "METADATA_EMBEDDINGS")

    return embeddings


def get_metadata_binarizers():
    return get_object("METADATA_BINARIZERS")


def delete_metadata_binarizer():
    delete_object("METADATA_BINARIZERS")


def existence_metadata_binarizers():
    return check_key_existence("METADATA_BINARIZERS")


def get_metadata_embeddings():
    return get_object("METADATA_EMBEDDINGS")


def delete_metadata_embeddings():
    delete_object("METADATA_EMBEDDINGS")


def existence_metadata_embeddings():
    return check_key_existence("METADATA_EMBEDDINGS")
