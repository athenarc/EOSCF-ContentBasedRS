import logging

import pandas as pd
from api.settings import APP_SETTINGS
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoDbConnector:
    def __init__(self, uri, db_name):
        self._uri = uri
        self._conn = None
        self._db_name = db_name
        self._db = None

    def get_db(self):
        return self._db

    def connect(self):
        try:
            logger.debug('Connecting to the Mongo database...')
            self._conn = MongoClient(self._uri)
            self._db = self._conn[self._db_name]

        except Exception as error:
            logger.error(error)


class RSMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(APP_SETTINGS["CREDENTIALS"]['RS_MONGO_URI'],
                                                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_DB'])
        self.mongo_connector.connect()

    # TODO get only attributes?
    def get_services(self, attributes=None, conditions=None):
        if conditions is None:
            conditions = {}
        if attributes is None:
            attributes = []

        services = pd.DataFrame(list(self.mongo_connector.get_db()["service"].find(conditions)))
        services.rename(columns={'_id': 'service_id'}, inplace=True)

        return services[["service_id"] + attributes]

    def get_scientific_domains(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["scientific_domain"].find({}, {"_id": 1})]

    def get_categories(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["category"].find({}, {"_id": 1})]

    def get_target_users(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["target_user"].find({}, {"_id": 1})]

    # TODO change it when i can get the info from recommender db
    def get_user_services(self, user_id):
        return []


class InternalMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_URI'],
                                                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_DATABASE'])
        self.mongo_connector.connect()
    # TODO: This is were functions like storing logging will be implemented
