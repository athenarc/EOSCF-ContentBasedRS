import logging

logger = logging.getLogger(__name__)


def ordering(services):
    """
    Ordering the services by score
    @param services: DataFrame, scores of services indexed by service id
    """
    logger.debug("Order services...")

    return services.sort_values(ascending=False)
