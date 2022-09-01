import logging

logger = logging.getLogger(__name__)


def ordering(resources):
    """
    Ordering the resources by score
    @param resources: DataFrame, scores of resources indexed by resource id
    """
    logger.debug("Order resources...")

    return resources.sort_values(ascending=False)
