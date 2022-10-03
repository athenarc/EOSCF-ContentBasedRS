import datetime
import logging

import pandas as pd
from api.settings import APP_SETTINGS
from pymongo import MongoClient

logger = logging.getLogger(__name__)


def form_mongo_url(username, password, host, port) -> str:
    uri = f"mongodb://{username}:{password}@" if username and password else ""
    uri += f"{host}:{port}"
    return uri


class MongoDbConnector:
    def __init__(self, uri, db_name):
        self._uri = uri
        print(self._uri)

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
        self.mongo_connector = MongoDbConnector(
            uri=form_mongo_url(
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_USERNAME'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_PASSWORD'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_HOST'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_PORT']
            ),
            db_name=APP_SETTINGS["CREDENTIALS"]['RS_MONGO_DATABASE']
        )
        self.mongo_connector.connect()

    # TODO get only attributes?
    def get_services(self, attributes=None, conditions=None):
        if conditions is None:
            conditions = {}
        if attributes is None:
            attributes = []

        services = list(self.mongo_connector.get_db()["service"].find(conditions))
        if len(services):
            servicesDf = pd.DataFrame(services)
            servicesDf.rename(columns={'_id': 'service_id'}, inplace=True)
            servicesDf = servicesDf[["service_id"] + attributes]
        else:  # If there are no services
            servicesDf = pd.DataFrame(columns=["service_id"] + attributes)

        return servicesDf

    def get_service(self, service_id):
        return self.mongo_connector.get_db()["service"].find_one({'_id': int(service_id)})

    def get_project(self, project_id):
        return self.mongo_connector.get_db()["project"].find_one({"_id": int(project_id)})

    def get_scientific_domains(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["scientific_domain"].find({}, {"_id": 1})]

    def get_categories(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["category"].find({}, {"_id": 1})]

    def get_target_users(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["target_user"].find({}, {"_id": 1})]

    def get_user_services(self, user_id):
        user_projects_services = self.mongo_connector.get_db()["project"].find({"user_id": user_id}, {"services": 1})
        user_services = set()
        for project_services in user_projects_services:
            user_services.update(project_services["services"])
        return list(user_services)

    def get_project_services(self, project_id):
        return self.mongo_connector.get_db()["project"].find_one({"_id": project_id})["services"]

    def get_projects(self):
        return [project["_id"] for project in self.mongo_connector.get_db()["project"].find({}, {"_id": 1})]

    def get_users(self, attributes=None):
        if attributes is None:
            attributes = {}

        return [user["_id"] for user in self.mongo_connector.get_db()["user"].find({}, attributes)]

    def is_valid_service(self, service_id):
        return self.get_service(service_id) is not None

    def is_valid_user(self, user_id):
        result = self.mongo_connector.get_db()["user"].find_one({"_id": int(user_id)})
        return result is not None

    def is_valid_project(self, project_id):
        return self.get_project(project_id) is not None


class InternalMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(
            uri=form_mongo_url(
                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_USERNAME'],
                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_PASSWORD'],
                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_HOST'],
                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_PORT']
            ),
            db_name=APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_DATABASE']
        )
        self.mongo_connector.connect()

    def save_recommendation(self, recommendation, user_id, service_id, history_service_ids):
        document = {
            "date": datetime.datetime.utcnow(),
            "version": APP_SETTINGS["BACKEND"]["VERSION_NAME"],
            "service_id": int(service_id),
            "recommendation": recommendation,
            "user_id": int(user_id) if user_id is not None else None,
            "history_service_ids": history_service_ids
        }

        self.mongo_connector.get_db()['recommendation'].insert_one(document)

        logger.debug("Recommendation was successfully saved!")

    def update_version(self):
        version = {
            "name": APP_SETTINGS["BACKEND"]["VERSION_NAME"],
            "similar_services": {
                "metadata": APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA"],
                "text_attributes": APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["TEXT_ATTRIBUTES"],
                "metadata_weight": APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["METADATA_WEIGHT"],
                "viewed_weight": APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["VIEWED_WEIGHT"],
                "sbert_model": APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SBERT"]["MODEL"]
            },
            "project_completion": {
                "min_support": APP_SETTINGS["BACKEND"]["PROJECT_COMPLETION"]["MIN_SUPPORT"],
                "min_confidence": APP_SETTINGS["BACKEND"]["PROJECT_COMPLETION"]["MIN_CONFIDENCE"]
            }

        }

        # Update the version if it exists or create a new version document
        self.mongo_connector.get_db()["version"].update_one({"name": version["name"]}, {"$set": version}, upsert=True)

        logger.debug("Recommender version was successfully saved!")
