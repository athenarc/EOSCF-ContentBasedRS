import logging

from api.databases.mongo import RSMongoDB
from api.recommender.project_completion.components.recommendation_cadidates import \
    get_recommendation_candidates

logger = logging.getLogger(__name__)


def create_recommendation(project_id, recommendations_num=5):

    # Get viewed project's services
    db = RSMongoDB()
    project_services = db.get_project_services(project_id)

    candidates = get_recommendation_candidates(project_services)

    return candidates[:recommendations_num] if len(candidates) > recommendations_num else candidates
