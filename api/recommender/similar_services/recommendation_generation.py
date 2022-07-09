import logging

from api.databases.mongo import RSMongoDB
from api.recommender.similar_services.components.filtering import filtering
from api.recommender.similar_services.components.ordering import ordering
from api.recommender.similar_services.components.recommendation_candidates import \
    get_recommendation_candidates
from api.recommender.similar_services.components.reranking import re_ranking

logger = logging.getLogger(__name__)


def create_recommendation(viewed_resource_id, recommendations_num=5, user_id=None):

    # TODO add them to version
    viewed_weight = 0.5
    metadata_weight = 0.5

    db = RSMongoDB()

    logger.info("Get user purchases...")
    purchases = list(map(str, db.get_user_services(user_id))) if user_id is not None else []

    candidates = get_recommendation_candidates(viewed_resource_id, purchased_resources=purchases,
                                               view_weight=viewed_weight, metadata_weight=metadata_weight)

    candidates = filtering(db, candidates, viewed_resource_id, purchases)

    candidates = ordering(candidates)

    re_ranking(candidates)

    return candidates[:recommendations_num].index.tolist()
