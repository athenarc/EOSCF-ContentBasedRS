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
            logger.info('Connecting to the Mongo database...')
            self._conn = MongoClient(self._uri)
            self._db = self._conn[self._db_name]

        except Exception as error:
            logger.error(error)


class RSMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(APP_SETTINGS["CREDENTIALS"]['RS_MONGO_URI'],
                                                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_DB'])

    def get_services(self, attributes=None, conditions=None):
        if conditions is None:
            conditions = {}
        if attributes is None:
            attributes = []

        self.mongo_connector.connect()
        services = pd.DataFrame(list(self.mongo_connector.get_db()["service"].find(conditions)))

        services.rename(columns={'_id': 'service_id'}, inplace=True)

        return services[["service_id"] + attributes]

    def get_scientific_domains(self):
        self.mongo_connector.connect()
        return [domain["_id"] for domain in self.mongo_connector.get_db()["scientific_domain"].find({}, {"_id": 1})]

    def get_categories(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["category"].find({}, {"_id": 1})]

    def get_target_users(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["target_user"].find({}, {"_id": 1})]

    def get_user_services(self, user_id):
        return []


class InternalMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_URI'],
                                                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_DATABASE'])

    # TODO: This is were functions like storing logging will be implemented
