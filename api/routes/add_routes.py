from api.routes import recommendation


def initialize_routes(app):
    app.include_router(recommendation.router)
