from app.exceptions import ModeDoesNotExist
from app.recommenders.autocompletion.update import FieldSuggestionUpdate
from app.recommenders.project_assistant.update import ProjectAssistantUpdate
from app.recommenders.project_completion.update import ProjectCompletionUpdate
from app.recommenders.similar_services.update import \
    ServicesRecommendationUpdate
from app.recommenders.update.update import AggregatedUpdate
from app.settings import APP_SETTINGS


def get_updater():
    if APP_SETTINGS["BACKEND"]["MODE"] == "PROVIDERS-RECOMMENDER":
        return AggregatedUpdate([FieldSuggestionUpdate()])
    elif APP_SETTINGS["BACKEND"]["MODE"] == "PORTAL-RECOMMENDER":
        return AggregatedUpdate([
            ServicesRecommendationUpdate(),
            ProjectAssistantUpdate(),
            ProjectCompletionUpdate()
        ])
    elif APP_SETTINGS["BACKEND"]["MODE"] == "SIMILAR_SERVICES_EVALUATION":
        return AggregatedUpdate([
            ServicesRecommendationUpdate()
        ])
    else:
        raise ModeDoesNotExist(f"Mode {APP_SETTINGS['BACKEND']['MODE']} is not recognised.")
