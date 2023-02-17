import logging

from app.databases.registry.registry_selector import get_registry
from app.exceptions import IdNotExists
from app.recommender.project_completion.components.recommendation_cadidates import \
    get_recommendation_candidates

logger = logging.getLogger(__name__)


def create_recommendation(project_id, recommendations_num=5):

    # Get viewed project's services
    db = get_registry()

    if not db.is_valid_project(project_id):
        raise IdNotExists("Project id does not exist.")

    project_services = db.get_project_services(project_id)

    candidates = get_recommendation_candidates(project_services)

    return candidates[:recommendations_num] if len(candidates) > recommendations_num else candidates
