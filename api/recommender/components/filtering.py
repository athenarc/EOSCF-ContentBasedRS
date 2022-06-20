import logging

logger = logging.getLogger(__name__)


def filtering(db, resources, viewing_resource, purchased_resources):
    """
    Filtering the candidate recommendations
    @param db: PostgresDB
    @param resources: DataFrame, scores of resources indexed by resource id
    @param viewing_resource:  str, the id of the currently viewing resource
    @param purchased_resources: list<str>, the ids of the user purchased resources
    """
    logger.info(f"Filter resources...")

    # Get non-published resources
    non_published_resources = list(map(str, db.get_services(conditions="status != 'published'")["service_id"].to_list()))

    # Get the indexes of viewing, purchased and non-published resources
    indexes_to_drop = list(set(non_published_resources + [viewing_resource] + purchased_resources))

    # Return
    return resources.drop(labels=indexes_to_drop)
