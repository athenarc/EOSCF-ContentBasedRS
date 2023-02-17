import logging
from typing import Optional

import pandas as pd
from app.databases.registry.registry_abc import Registry
from app.databases.utils.mongo_connector import (MongoDbConnector,
                                                 form_mongo_url)
from app.settings import APP_SETTINGS
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class RSMongoDB(Registry):
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

    def check_health(self) -> Optional[str]:
        # Check that all the required collections exist in the RS Mongo
        collections = ['service', 'project', 'scientific_domain', 'category', 'target_user', 'user']

        try:
            collection_list = self.mongo_connector.get_db().list_collection_names()
        except ServerSelectionTimeoutError:
            error = "Could not establish connection with RS mongo"
            logger.error(error)
            return error

        missing_collections = []
        for collection in collections:
            if collection not in collection_list:
                logger.error(f"Could not find collection {collection}")
                missing_collections.append(collection)

        return f"Collections {' '.join(missing_collections)} are missing" if len(missing_collections) != 0 else None

    def get_services_by_ids(self, ids, attributes=None):
        return self.get_services(attributes=attributes, conditions={'_id': {'$in': ids}})

    # TODO get only attributes?
    def get_services(self, attributes=None, conditions=None):
        if conditions is None:
            conditions = {}
        if attributes is None:
            attributes = []

        services = list(self.mongo_connector.get_db()["service"].find(conditions))
        if len(services):
            services_df = pd.DataFrame(services)
            services_df.rename(columns={'_id': 'service_id'}, inplace=True)
            services_df = services_df[list(set(["service_id"] + attributes))]
        else:  # If there are no services
            services_df = pd.DataFrame(columns=list(set(["service_id"] + attributes)))

        self._remove_general_attributes_from_services(services_df)

        return services_df

    def get_non_published_services(self, considered_services=None):
        conditions = {"status": {"$ne": "published"}}
        if considered_services is not None:
            conditions["_id"]  = {'$in': considered_services}
        return list(self.get_services(conditions=conditions)["service_id"].to_list())

    def get_service(self, service_id):
        service = self.mongo_connector.get_db()["service"].find_one({'_id': int(service_id)})
        self._remove_general_attributes_from_single_service(service)
        return service

    def get_project(self, project_id):
        return self.mongo_connector.get_db()["project"].find_one({"_id": int(project_id)})

    def get_scientific_domains(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["scientific_domain"].find({}, {"_id": 1})]

    def get_categories(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["category"].find({}, {"_id": 1})]

    def get_target_users(self):
        return [domain["_id"] for domain in self.mongo_connector.get_db()["target_user"].find({}, {"_id": 1})]

    def _get_general_attribute_ids(self):
        return {
            "scientific_domains": {
                domain["_id"]
                for domain in self.mongo_connector.get_db()["scientific_domain"].find({"name": "Other"}, {"_id": 1})
            },
            "categories": {
                category["_id"]
                for category in self.mongo_connector.get_db()["category"].find({"name": "Other"}, {"_id": 1})
            },
            "target_users": {
                target_user["_id"]
                for target_user in self.mongo_connector.get_db()["target_user"].find({"name": "Other"}, {"_id": 1})
            }
        }

    def _remove_general_attributes_from_services(self, services):
        general_attribute_ids = self._get_general_attribute_ids()

        for attribute, ids in general_attribute_ids.items():
            if attribute in services:
                services[attribute] = services[attribute].apply(lambda x: list(set(x).difference(ids)))

    def _remove_general_attributes_from_single_service(self, service):
        general_attribute_ids = self._get_general_attribute_ids()

        for attribute, ids in general_attribute_ids.items():
            if attribute in service:
                service[attribute] = list(set(service[attribute]).difference(ids))

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
