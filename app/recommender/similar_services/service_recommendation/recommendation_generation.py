import logging

from app.databases.content_based_rec_db import ContentBasedRecsMongoDB
from app.databases.registry.registry_selector import get_registry
from app.exceptions import IdNotExists
from app.recommender.similar_services.service_recommendation.components.filtering import \
    filtering
from app.recommender.similar_services.service_recommendation.components.ordering import \
    ordering
from app.recommender.similar_services.service_recommendation.components.reranking import \
    re_ranking
from app.recommender.similar_services.service_recommendation.components.resources_similarity import \
    resources_similarity
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


def create_recommendation(viewed_resource_id, recommendations_num=5, user_id=None,
                          viewed_weight=None, metadata_weight=None):
    viewed_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"] \
        if viewed_weight is None else viewed_weight
    metadata_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"] \
        if metadata_weight is None else metadata_weight

    db = get_registry()

    service_exists(db, viewed_resource_id)

    user = User(user_id)
    purchases = user.get_purchases()

    candidates = resources_similarity(viewed_resource_id,
                                      purchased_resources=purchases,
                                      view_weight=viewed_weight,
                                      metadata_weight=metadata_weight)

    candidates = filtering(db, candidates, viewed_resource_id, purchases)

    candidates = ordering(candidates)

    candidates = re_ranking(target_service=viewed_resource_id,
                            purchases=purchases,
                            candidates=candidates,
                            recommendations_num=recommendations_num,
                            viewed_weight=viewed_weight,
                            metadata_weight=metadata_weight
                            )

    recommendation = [{"service_id": service_id, "score": score} for service_id, score in
                      candidates[:recommendations_num].items()]

    content_based_recs_db = ContentBasedRecsMongoDB()
    content_based_recs_db.save_recommendation(recommendation=recommendation, service_id=viewed_resource_id,
                                              user_id=user_id, history_service_ids=purchases)

    return recommendation
