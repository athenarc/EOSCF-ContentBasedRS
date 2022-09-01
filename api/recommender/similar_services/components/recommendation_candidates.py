import logging

import numpy as np
import pandas as pd
from api.recommender.similar_services.initialization import (
    metadata_structure, text_structure)

logger = logging.getLogger(__name__)


# TODO: use of purchase time?
def get_recommendation_candidates(view_resource, purchased_resources, view_weight=0.5, metadata_weight=0.5):
    """
    Creates a structure with the score of each resource based on the viewing and purchased resources
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
    logger.debug("Calculating similarities...")
    metadata_similarities = metadata_structure.get_metadata_similarities()
    text_similarities = text_structure.get_text_similarities()

    # Initialize weights
    indexing = metadata_similarities.index.to_list()
    weights = pd.Series(np.zeros(metadata_similarities.shape[0]), index=indexing)

    # Add the weights of view_resource and purchased resources
    if len(purchased_resources) > 0:
        weights.loc[purchased_resources] = (1-view_weight)*(1/len(purchased_resources))
        weights.loc[str(view_resource)] = view_weight
    else:
        weights.loc[str(view_resource)] = 1.0

    # Calculate the metadata and text similarity of each resource
    metadata_similarity = pd.Series(np.average(metadata_similarities, weights=weights, axis=1),
                                    index=indexing)
    text_similarity = pd.Series(np.average(text_similarities, weights=weights, axis=1),
                                index=indexing)

    # Calculate the weighted average of the similarities
    candidates = pd.Series(np.average(pd.concat([metadata_similarity, text_similarity], axis=1),
                                      weights=[metadata_weight, 1-metadata_weight], axis=1), index=indexing)

    return candidates
