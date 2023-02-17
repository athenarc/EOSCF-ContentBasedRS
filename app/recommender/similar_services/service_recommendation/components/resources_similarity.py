import logging

import numpy as np
import pandas as pd
from app.recommender.similar_services.preprocessor.similarities.metadata_similarities import \
    get_metadata_similarities
from app.recommender.similar_services.preprocessor.similarities.text_similarities import \
    get_text_similarities

logger = logging.getLogger(__name__)


# TODO: use of purchase time?
def resources_similarity(resource, compared_resources=None, purchased_resources=None,
                         view_weight=0.5, metadata_weight=0.5):
    """
    Creates a structure with the similarity of each resource with the viewing and purchased resources
    Score of resource i S_i = metadata_weight * metadata_similarity(i, viewed_resource, purchased_resources) +
                              (1-metadata_weight) * text_similarity(i, viewed_resource, purchased_resources)
    , where <>_similarity(i, view_resource, purchased_resources) = view_weight * sim(i, view_resource) +
                                                                   (1-view_weight) * avg(sim(i, purchased_resource_j))
    Args:
        resource: the id of the resource to be compared
        purchased_resources: list, the ids of the user purchased resources that need to be considered
        compared_resources: list, the list of ids of the resources for which we want to calculate the similarity. If None, all resources are considered
        view_weight: float [0,1], the weight of the viewed resource similarity in the score calculation
        metadata_weight: float [0,1], the weight of the metadata similarity in the score calculation

    Returns:

    """
    logger.debug("Calculating resources similarities...")
    metadata_similarities = get_metadata_similarities()
    text_similarities = get_text_similarities()

    if purchased_resources is None:
        purchased_resources = []

    # # Filter resources based on compared_resources
    if compared_resources is not None:
        considered_resources = [resource]+purchased_resources+compared_resources
        metadata_similarities = metadata_similarities.loc[considered_resources, considered_resources]
        text_similarities = text_similarities.loc[considered_resources, considered_resources]

    # Initialize weights
    indexing = metadata_similarities.index.to_list()
    weights = pd.Series(np.zeros(metadata_similarities.shape[0]), index=indexing)

    # Add the weights of view_resource and purchased resources
    if len(purchased_resources) > 0:
        weights.loc[purchased_resources] = (1-view_weight)*(1/len(purchased_resources))
        weights.loc[resource] = view_weight
    else:
        weights.loc[resource] = 1.0

    # Calculate the metadata and text similarity of each resource
    metadata_similarity = pd.Series(np.average(metadata_similarities, weights=weights, axis=1),
                                    index=indexing)
    text_similarity = pd.Series(np.average(text_similarities, weights=weights, axis=1),
                                index=indexing)

    # Calculate the weighted average of the similarities
    candidates = pd.Series(np.average(pd.concat([metadata_similarity, text_similarity], axis=1),
                                      weights=[metadata_weight, 1-metadata_weight], axis=1), index=indexing)

    return candidates.drop([resource]+purchased_resources)
