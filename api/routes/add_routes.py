from api.routes import (auto_completion, health, project_completion,
                        similar_services, update, project_assistant)
from api.settings import APP_SETTINGS


def initialize_routes(app):
    if APP_SETTINGS['BACKEND']['MODE'] == 'RS':
        app.include_router(health.router)  # Only implemented health checks for the RS
        app.include_router(similar_services.router)
        app.include_router(project_assistant.router)
        app.include_router(project_completion.router)

    if APP_SETTINGS['BACKEND']['MODE'] == 'AUTO-COMPLETION':
        app.include_router(auto_completion.router)

    app.include_router(update.router)
