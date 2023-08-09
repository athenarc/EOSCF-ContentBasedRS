import logging

import numpy as np
import pandas as pd
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.similarities.metadata_similarities import \
    MetadataSimilaritiesManager
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.similarities.text_similarities import \
    TextSimilaritiesManager

logger = logging.getLogger(__name__)


# TODO: use of purchase time?
def services_similarity(service, compared_services=None, purchased_services=None,
                        view_weight=0.5, metadata_weight=0.5):
    """
    Creates a structure with the similarity of each service with the viewing and purchased services
    Score of service i S_i = metadata_weight * metadata_similarity(i, viewed_service, purchased_services) +
                              (1-metadata_weight) * text_similarity(i, viewed_service, purchased_services)
    , where <>_similarity(i, view_service, purchased_services) = view_weight * sim(i, view_service) +
                                                                   (1-view_weight) * avg(sim(i, purchased_service_j))
    Args:
        service: the id of the service to be compared
        purchased_services: list, the ids of the user purchased services that need to be considered
        compared_services: list, the list of ids of the services for which we want to calculate the similarity.
                           If None, all services are considered
        view_weight: float [0,1], the weight of the viewed service similarity in the score calculation
        metadata_weight: float [0,1], the weight of the metadata similarity in the score calculation

    Returns:

    """
    logger.debug("Calculating services similarities...")
    metadata_similarities = MetadataSimilaritiesManager().get_similarities()
    text_similarities = TextSimilaritiesManager().get_similarities()

    if purchased_services is None:
        purchased_services = []

    # # Filter services based on compared_services
    if compared_services is not None:
        considered_services = [service] + purchased_services + compared_services
        metadata_similarities = metadata_similarities.loc[considered_services, considered_services]
        text_similarities = text_similarities.loc[considered_services, considered_services]

    # Initialize weights
    indexing = metadata_similarities.index.to_list()
    weights = pd.Series(np.zeros(metadata_similarities.shape[0]), index=indexing)

    # Add the weights of view_service and purchased services
    if len(purchased_services) > 0:
        weights.loc[purchased_services] = (1 - view_weight) * (1 / len(purchased_services))
        weights.loc[service] = view_weight
    else:
        weights.loc[service] = 1.0

    # Calculate the metadata and text similarity of each service
    metadata_similarity = pd.Series(np.average(metadata_similarities, weights=weights, axis=0),
                                    index=indexing)
    text_similarity = pd.Series(np.average(text_similarities, weights=weights, axis=0),
                                index=indexing)

    # Calculate the weighted average of the similarities
    candidates = pd.Series(np.average(pd.concat([metadata_similarity, text_similarity], axis=1),
                                      weights=[metadata_weight, 1 - metadata_weight], axis=1), index=indexing)

    return candidates.drop([service] + purchased_services)
