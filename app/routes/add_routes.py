from app.routes import (auto_completion, health, project_assistant,
                        project_completion, similar_services, update, tags_recommender)
from app.settings import APP_SETTINGS


def initialize_routes(app):

    app.include_router(health.router)

    if APP_SETTINGS['BACKEND']['MODE'] == 'PORTAL-RECOMMENDER':
        app.include_router(similar_services.router)
        app.include_router(project_assistant.router)
        app.include_router(project_completion.router)

    if APP_SETTINGS['BACKEND']['MODE'] == 'PROVIDERS-RECOMMENDER':
        app.include_router(auto_completion.router)
        app.include_router(tags_recommender.router)

    app.include_router(update.router)
