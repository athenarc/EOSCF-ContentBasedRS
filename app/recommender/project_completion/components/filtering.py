import logging

from app.databases.registry.registry_selector import get_registry

logger = logging.getLogger(__name__)


def filtering(candidate_resources):
    """
    Filtering the candidate recommendations
    """
    logger.debug(f"Filter resources...")

    # Get the information of each candidate resource
    resources_ids = [candidate["service_id"] for candidate in candidate_resources]
    db = get_registry()
    resources_info = db.get_services(attributes=['status'], conditions={'_id': {'$in': resources_ids}})

    # Filter non-published resources
    valid_resources = resources_info[resources_info["status"] == "published"]["service_id"].tolist()
    candidate_resources = list(filter(lambda x: x["service_id"] in valid_resources, candidate_resources))

    return candidate_resources
