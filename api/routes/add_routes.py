from api.routes import recommendations


def initialize_routes(app):
    app.include_router(recommendations.router)
