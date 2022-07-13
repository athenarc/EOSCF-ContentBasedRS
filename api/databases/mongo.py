import datetime
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
        logger.debug('Connecting to the Mongo database...')
        self._conn = MongoClient(self._uri)
        self._db = self._conn[self._db_name]


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

    def get_users(self, attributes=None):
        if attributes is None:
            attributes = {}

        return [user["_id"] for user in self.mongo_connector.get_db()["user"].find({}, attributes)]

    def is_valid_service(self, service_id):
        result = self.mongo_connector.get_db()["service"].find({'_id': int(service_id)}, {"_id": 1}).limit(1)
        return len(list(result)) == 1

    def is_valid_user(self, user_id):
        result = self.mongo_connector.get_db()["user"].find({"_id": int(user_id)}, {"_id": 1}).limit(1)
        return len(list(result)) == 1


class InternalMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_URI'],
                                                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_DATABASE'])
        self.mongo_connector.connect()

    # TODO: This is were functions like storing logging will be implemented
    def save_recommendation(self, recommendation, user_id, service_id, history_service_ids):
        document = {
            "date": datetime.datetime.utcnow(),
            # TODO: change it when versioning is available
            "version": "1.0",
            "service_id": service_id,
            "version": "1.0",
            "service_id": int(service_id),
            "recommendation": recommendation,
            "user_id": int(user_id),
            "history_service_ids": history_service_ids
        }

        document_id = self.mongo_connector.get_db()['recommendation'].insert_one(document)

        logger.info("Recommendation was successfully saved!")
