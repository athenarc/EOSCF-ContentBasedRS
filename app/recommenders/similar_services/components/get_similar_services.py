import logging

from app.databases.registry.registry_selector import get_registry
from app.exceptions import IdNotExists
from app.recommenders.algorithms.similar_services_retrieval.services_similarity import \
    services_similarity
from app.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


class User:
    def __init__(self, user_id):
        # TODO: Currently if a user_id does not exist we consider the user as anonymous
        # TODO: Required from front since a new user will not exist in the RS Mongo yet
        self.user_id = user_id if self.is_valid_user(user_id) else None
        self.registered_user = True if self.user_id is not None else False

    @staticmethod
    def is_valid_user(user_id):
        """
        Return True if the user_id exists or is None (anonymous), otherwise return False
        """
        if user_id is not None and not get_registry().is_valid_user(user_id):
            return False

        return True

    def get_purchases(self):
        logger.debug("Get user purchases...")
        if self.registered_user:
            return list(get_registry().get_user_services(self.user_id))
        else:
            return []


def service_exists(db, viewed_service_id):
    """
    Checks if the given service id exists
    """
    if not db.is_valid_service(viewed_service_id):
        raise IdNotExists("Service id does not exist.")


def get_similar_services(service_id, user_id=None, compared_services=None):
    viewed_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"]
    metadata_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"]

    db = get_registry()

    service_exists(db, service_id)

    user = User(user_id)
    purchases = user.get_purchases()

    return services_similarity(service_id, compared_services, purchases,
                               metadata_weight=metadata_weight, view_weight=viewed_weight)
