import logging

from app.databases.registry.registry_selector import get_registry

logger = logging.getLogger(__name__)


def filtering(candidate_services):
    """
    Filtering the candidate recommendations
    """
    logger.debug(f"Filter services...")

    # Get the information of each candidate service
    services_ids = [candidate["service_id"] for candidate in candidate_services]
    db = get_registry()
    services_info = db.get_services(attributes=['status'], conditions={'_id': {'$in': services_ids}})

    # Filter non-published services
    valid_services = services_info[services_info["status"] == "published"]["service_id"].tolist()
    candidate_services = list(filter(lambda x: x["service_id"] in valid_services, candidate_services))

    return candidate_services
