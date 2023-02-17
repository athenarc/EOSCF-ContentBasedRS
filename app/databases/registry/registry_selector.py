from app.databases.registry.catalog_api import CatalogueAPI
from app.databases.registry.catalog_dump import CatalogueDump
from app.databases.registry.rs_mongo import RSMongoDB
from app.settings import APP_SETTINGS


def get_registry():
    if APP_SETTINGS['BACKEND']['MODE'] == 'PORTAL-RECOMMENDER':
        return RSMongoDB()
    elif APP_SETTINGS['BACKEND']['MODE'] == 'PROVIDERS-RECOMMENDER':
        return CatalogueAPI()
    elif APP_SETTINGS['BACKEND']['MODE'] == "SIMILAR_SERVICES_EVALUATION":
        return CatalogueDump()
    else:
        pass  # TODO raise error
