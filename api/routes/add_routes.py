from api.routes import similar_services, update


def initialize_routes(app):
    app.include_router(similar_services.router)
    app.include_router(update.router)
