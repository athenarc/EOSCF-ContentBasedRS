from app.recommender.project_completion.update import ProjectCompletionUpdate
from app.recommender.similar_services.field_suggestion.update import \
    FieldSuggestionUpdate
from app.recommender.similar_services.project_assistant.update import \
    ProjectAssistantUpdate
from app.recommender.similar_services.service_recommendation.update import \
    ServicesRecommendationUpdate
from app.recommender.update.update import AggregatedUpdate
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
        pass  # TODO raise error
