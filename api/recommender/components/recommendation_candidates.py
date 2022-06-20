import pandas as pd
import numpy as np
import logging

from api.recommender.initialization.metadata_structure import METADATA_STRUCTURES
from api.recommender.initialization.text_structure import TEXT_STRUCTURES

logger = logging.getLogger(__name__)


# TODO: use of purchase time?
def get_recommendation_candidates(view_resource, purchased_resources, view_weight=0.5, metadata_weight=0.5):
    """
    Creates the a structure with the score of each resource based on the viewing and purchased resources
    Score of resource i S_i = metadata_weight * metadata_similarity(i, viewed_resource, purchased_resources) +
                              (1-metadata_weight) * text_similarity(i, viewed_resource, purchased_resources)
    , where <>_similarity(i, view_resource, purchased_resources) = view_weight * sim(i, view_resource) +
                                                                   (1-view_weight) * avg(sim(i, purchased_resource_j))
    @param view_resource: str, the id of the currently viewing resource
    @param purchased_resources: list<str>, the ids of the user purchased resources
    @param view_weight: float [0,1], the weight of the viewed resource similarity in the score calculation
    @param metadata_weight: float [0,1], the weight of the metadata similarity in the score calculation
    @return:
    """
    logger.info("Calculate similarities...")

    # Initialize weights
    indexing = METADATA_STRUCTURES.embeddings.index.to_list()
    weights = pd.Series(np.zeros(METADATA_STRUCTURES.similarities.shape[0]), index=indexing)
    # Add the weight of the view_resource
    weights.loc[view_resource] = view_weight
    # Add the weights of each purchased resource
    if len(purchased_resources) > 0:
        weights.loc[purchased_resources] = (1-view_weight)*(1/len(purchased_resources))

    # Calculate the metadata and text similarity of each resource
    metadata_similarity= pd.Series(np.average(METADATA_STRUCTURES.similarities, weights=weights, axis=1), index=indexing)
    text_similarity = pd.Series(np.average(TEXT_STRUCTURES.similarities, weights=weights, axis=1), index=indexing)

    # Calculate the weighted average of the similarities
    candidates = pd.Series(np.average(pd.concat([metadata_similarity, text_similarity], axis=1),
                                      weights=[metadata_weight, 1-metadata_weight], axis=1), index=indexing)

    return candidates
