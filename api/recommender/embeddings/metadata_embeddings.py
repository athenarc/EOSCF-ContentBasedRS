import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from pickle import dump

from api.settings import APP_SETTINGS


# TODO: delete binarizers??
def create_metadata_embeddings(resources, db):
    """
    Creates the metadata-based embeddings of each resource
    @param resources:
    @param db: PostgresDB
    @return: Dataframe
    """

    partial_embeddings = []
    binarizers = {}

    # e.g., attribute = scientific_domains
    for attribute in APP_SETTINGS['METADATA']:
        # Initialize binarizers
        binarizers[attribute] = MultiLabelBinarizer(classes=getattr(db, "get_"+attribute)())
        # Transform resources attribute to one-hot encoding
        partial_embeddings.append(binarizers[attribute].fit_transform(resources[attribute]))

    # save the binarizers
    for attribute, binarizer in binarizers.items():
        dump(binarizer, open(attribute + '_binarizer.pkl', 'wb'))

    # Concatenate the embeddings of all attributes
    embeddings = pd.DataFrame(data=np.concatenate(tuple(partial_embeddings), axis=1), index=resources["service_id"].to_list())
    embeddings.columns = embeddings.columns.astype(str)

    return embeddings
