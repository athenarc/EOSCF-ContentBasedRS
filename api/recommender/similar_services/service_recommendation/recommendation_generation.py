import logging

from api.databases.content_based_rec_db import ContentBasedRecsMongoDB
from api.databases.registry.registry_selector import get_registry
from api.exceptions import IdNotExists
from api.recommender.similar_services.service_recommendation.components.filtering import \
    filtering
from api.recommender.similar_services.service_recommendation.components.ordering import \
    ordering
from api.recommender.similar_services.service_recommendation.components.recommendation_candidates import \
    get_recommendation_candidates
from api.recommender.similar_services.service_recommendation.components.reranking import \
    re_ranking
from api.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


def service_exists(db, viewed_service_id):
    """
    Checks if the given service id exists
    """
    if not db.is_valid_service(viewed_service_id):
        raise IdNotExists("Service id does not exist.")


def valid_user(db, user_id):
    """
    Return the user_id if user_id is valid else None
    """
    if user_id is not None and not db.is_valid_user(user_id):
        return None
    return user_id


def create_recommendation(viewed_resource_id, recommendations_num=5, user_id=None,
                          viewed_weight=None, metadata_weight=None):
    viewed_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"] \
        if viewed_weight is None else viewed_weight
    metadata_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"] \
        if metadata_weight is None else metadata_weight

    db = get_registry()

    service_exists(db, viewed_resource_id)

    user_id = valid_user(db, user_id)

    logger.debug("Get user purchases...")
    purchases = list(db.get_user_services(user_id)) if user_id is not None else []

    candidates = get_recommendation_candidates(viewed_resource_id,
                                               purchased_resources=purchases,
                                               view_weight=viewed_weight,
                                               metadata_weight=metadata_weight)

    candidates = filtering(db, candidates, viewed_resource_id, purchases)

    candidates = ordering(candidates)

    candidates = re_ranking(target_service=viewed_resource_id, candidates=candidates,
                            recommendations_num=recommendations_num)

    recommendation = [{"service_id": service_id, "score": score} for service_id, score in
                      candidates[:recommendations_num].items()]

    content_based_recs_db = ContentBasedRecsMongoDB()
    content_based_recs_db.save_recommendation(recommendation=recommendation, service_id=viewed_resource_id,
                                              user_id=user_id, history_service_ids=purchases)

    return recommendation
