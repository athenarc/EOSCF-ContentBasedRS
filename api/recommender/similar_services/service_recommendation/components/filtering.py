import logging

from api.databases.redis_db import get_object

logger = logging.getLogger(__name__)


def unhealthy_resources(resources):
    # TODO: Get resources ids to drop unhealthy resources from list
    _status_report = get_object('STATUS_REPORT')
    _ar_report = get_object('AR_REPORT')

    pass


def filtering(db, resources, viewing_resource, purchased_resources):
    """
    Filtering the candidate recommendations
    @param db: Database
    @param resources: DataFrame, scores of resources indexed by resource id./
    @param viewing_resource:  str, the id of the currently viewing resource
    @param purchased_resources: list<str>, the ids of the user purchased resources
    """
    logger.debug(f"Filter resources...")

    # Get non-published resources
    non_published_resources = db.get_non_published_services()

    # Get the indexes of viewing, purchased and non-published resources
    indexes_to_drop = list(set(non_published_resources + [viewing_resource] + purchased_resources))

    return resources.drop(labels=indexes_to_drop)
