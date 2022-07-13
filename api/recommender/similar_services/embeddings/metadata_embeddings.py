import os
from pickle import dump

import numpy as np
import pandas as pd
from api.settings import APP_SETTINGS
from sklearn.preprocessing import MultiLabelBinarizer


def create_metadata_embeddings(resources, db):
    """
    Creates the metadata-based embeddings of each resource
    @param resources:
    @param db: PostgresDB
    @return: Dataframe
    """

    binarizers_dir = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["BINARIZERS_STORAGE_PATH"]

    # Delete binarizers if they exist
    for f in os.listdir(binarizers_dir):
        if f != '.gitkeep':
            os.remove(os.path.join(binarizers_dir, f))

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
    for attribute, binarizer in binarizers.items():
        dump(binarizer, open(binarizers_dir + "/" + attribute + '_binarizer.pkl', 'wb'))

    # Concatenate the embeddings of all attributes
    embeddings = pd.DataFrame(data=np.concatenate(tuple(partial_embeddings), axis=1),
                              index=resources["service_id"].to_list())
    embeddings.columns = embeddings.columns.astype(str)

    return embeddings
