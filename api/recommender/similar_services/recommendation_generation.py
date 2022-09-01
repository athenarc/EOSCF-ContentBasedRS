import logging

from api.databases.mongo import InternalMongoDB, RSMongoDB
from api.recommender.similar_services.components.filtering import filtering
from api.recommender.similar_services.components.ordering import ordering
from api.recommender.similar_services.components.recommendation_candidates import \
    get_recommendation_candidates
from api.recommender.similar_services.components.reranking import re_ranking
from api.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


class IdNotExists(Exception):
    """ Will be thrown when the queried id was not found """
    pass


def arguments_exist(db, viewed_service_id, user_id):
    """
    Checks if the given service id and user id exists
    """
    if not db.is_valid_service(viewed_service_id):
        raise IdNotExists("Service id does not exist.")

    if not db.is_valid_user(user_id):
        raise IdNotExists("User id does not exist.")


def create_recommendation(viewed_resource_id, recommendations_num=5, user_id=None):

    viewed_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"]
    metadata_weight = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"]

    db = RSMongoDB()

    arguments_exist(db, viewed_resource_id, user_id)

    logger.debug("Get user purchases...")
    purchases = list(map(str, db.get_user_services(user_id))) if user_id is not None else []

    candidates = get_recommendation_candidates(viewed_resource_id, purchased_resources=purchases,
                                               view_weight=viewed_weight, metadata_weight=metadata_weight)

    candidates = filtering(db, candidates, viewed_resource_id, purchases)

    candidates = ordering(candidates)

    # TODO: implement
    re_ranking(candidates)

    recommendation = [{"service_id": int(service_id), "score": score} for service_id, score in
                      candidates[:recommendations_num].items()]

    # if APP_SETTINGS['BACKEND']['PROD']:
    internal_db = InternalMongoDB()
    internal_db.save_recommendation(recommendation=recommendation, service_id=viewed_resource_id, user_id=user_id,
                                    history_service_ids=purchases)

    return recommendation

# def test_recommendation(viewed_resource_id, purchases, recommendations_num=5, viewed_weight=0.5, metadata_weight=0.5):
#     db = PostgresDb(APP_SETTINGS["CREDENTIALS"])
#     db.connect()
#
#     candidates = get_recommendation_candidates(viewed_resource_id, purchased_resources=purchases,
#                                                view_weight=viewed_weight, metadata_weight=metadata_weight)
#
#     candidates = filtering(db, candidates, viewed_resource_id, purchases)
#
#     db.close_connection()
#
#     candidates = ordering(candidates)
#
#     re_ranking(candidates)
#
#     return candidates[:recommendations_num].index.tolist()
