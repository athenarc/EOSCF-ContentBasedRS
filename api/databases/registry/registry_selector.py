from api.databases.registry.catalog_api import CatalogueAPI
from api.databases.registry.rs_mongo import RSMongoDB
from api.databases.registry.catalog_dump import CatalogueDump
from api.settings import APP_SETTINGS


def get_registry():
    if APP_SETTINGS['BACKEND']['MODE'] == 'RS':
        return RSMongoDB()
    elif APP_SETTINGS['BACKEND']['MODE'] == 'AUTO-COMPLETION':
        return CatalogueAPI()
    elif APP_SETTINGS['BACKEND']['MODE'] == "SIMILAR_SERVICES_EVALUATION":
        return CatalogueDump()
    else:
        pass  # TODO raise error
