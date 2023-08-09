import logging

from app.databases.registry.registry_selector import get_registry
from app.recommenders.similar_services.components.filtering import filtering
from app.recommenders.similar_services.components.get_similar_services import \
    get_similar_services
from app.recommenders.similar_services.components.ordering import ordering
from app.recommenders.similar_services.components.rec_logging import \
    store_recommendation
from app.recommenders.similar_services.components.reranking import re_ranking

logger = logging.getLogger(__name__)


def create_recommendation_set(viewed_service_id, recommendations_num=5, user_id=None, do_rerank=True):
    db = get_registry()

    candidates = get_similar_services(viewed_service_id, user_id=user_id)

    candidates = filtering(db, candidates)

    candidates = ordering(candidates)

    if do_rerank is True:
        candidates = re_ranking(
            candidates=candidates,
            recommendations_num=recommendations_num
        )

    recommendation_set = [{"service_id": service_id, "score": score} for service_id, score in
                          candidates[:recommendations_num].items()]

    store_recommendation(recommendation_set=recommendation_set, viewed_service_id=viewed_service_id, user_id=user_id)

    return recommendation_set
