from api.routes import project_completion, similar_services, update


def initialize_routes(app):
    app.include_router(similar_services.router)
    app.include_router(project_completion.router)
    app.include_router(update.router)
