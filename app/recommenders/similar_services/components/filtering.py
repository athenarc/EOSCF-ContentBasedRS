import logging

from app.databases.redis_db import get_object

logger = logging.getLogger(__name__)


def unhealthy_services(services):
    # TODO: Get services ids to drop unhealthy services from list
    _status_report = get_object('STATUS_REPORT')
    _ar_report = get_object('AR_REPORT')

    pass


def filtering(db, services):
    """
    Filtering the candidate recommendations
    @param db: Database
    @param services: DataFrame, scores of services indexed by service id./
    @param viewing_service:  str, the id of the currently viewing service
    @param purchased_services: list<str>, the ids of the user purchased services
    """
    logger.debug(f"Filter services...")

    # Get non-published services ids
    non_published_services = db.get_non_published_services()

    # Remove every non-published service existing in the services and return them
    return services.drop(labels=non_published_services, errors='ignore')
