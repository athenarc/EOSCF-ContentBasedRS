import pandas as pd
import requests
from app.databases.registry.registry_abc import Registry
from app.databases.utils.mongo_connector import (MongoDbConnector,
                                                 form_mongo_url)
from app.exceptions import APIResponseFormatException
from app.settings import APP_SETTINGS
from pymongo import MongoClient


class CatalogueDump(Registry):

    def __init__(self):
        self.mongo_connector = MongoDbConnector(
            uri=form_mongo_url(
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_USERNAME'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_PASSWORD'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_HOST'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_PORT']
            ),
            db_name="catalog_dump"
        )
        self.mongo_connector.connect()

    @staticmethod
    def _reformat_service(service):
        # Get only the leaves for each field with hierarchy levels
        service["scientificDomains"] = [item["scientificSubdomain"] for item in service["scientificDomains"]]
        service["categories"] = [item["subcategory"] for item in service["categories"]]

        # Rename the fields used in metadata to the global naming
        service["scientific_domains"] = service.pop("scientificDomains")
        service["target_users"] = service.pop("targetUsers")

        return service

    def get_services_by_ids(self, ids, attributes=None, conditions=None):
        return self.get_services(attributes=attributes, conditions={'id': {'$in': ids}})

    def get_services(self, attributes=None, conditions=None, reformat=True):
        """
        Args:
            attributes: list, the requested attributes for the services
            reformat: boolean, when true services attributes are reformated to be independent of the selected registry
        """
        if attributes is None:
            attributes = []

        services = list(self.mongo_connector.get_db()["service"].find(conditions))

        if reformat:
            services = [self._reformat_service(service) for service in services]

        if len(services):
            services_df = pd.DataFrame(services)
            services_df.rename(columns={'id': 'service_id'}, inplace=True)
            services_df = services_df[list(set(["service_id"] + attributes))]
        else:  # If there are no services
            services_df = pd.DataFrame(columns=list(set(["service_id"] + attributes)))

        self._remove_general_attributes_from_services(services_df)

        return services_df

    def get_service(self, service_id, reformat=True):
        service = self.mongo_connector.get_db()["service"].find_one({'id': service_id})
        if reformat and service is not None:
            service = self._reformat_service(service)
        self._remove_general_attributes_from_single_service(service)
        return service

    def get_scientific_domains(self):
        return [domain["id"] for domain in self.mongo_connector.get_db()["scientific_domain"].find({}, {"id": 1})]

    def get_categories(self):
        return [domain["id"] for domain in self.mongo_connector.get_db()["category"].find({}, {"id": 1})]

    def get_target_users(self):
        return [domain["id"] for domain in self.mongo_connector.get_db()["target_user"].find({}, {"id": 1})]

    def _remove_general_attributes_from_services(self, services):
        attributes = ['scientific_domains', 'categories', 'target_users']

        def remove_fields_containing_other(attribute_values):
            return [attr for attr in attribute_values if '-other-other' not in attr and 'generic' not in attr]

        for attribute in attributes:
            if attribute in services:
                services[attribute] = services[attribute].apply(remove_fields_containing_other)

    def _remove_general_attributes_from_single_service(self, service):
        attributes = ['scientific_domains', 'categories', 'target_users']

        for attribute in attributes:
            if attribute in service:
                service[attribute] = [attr for attr in service[attribute] if '-other-other' not in attr and 'generic' not in attr]

    def is_valid_service(self, service_id):
        return self.get_service(service_id) is not None


def _get_request(request):
    response = requests.get(request)

    if response.status_code != 200:
        raise APIResponseFormatException("Problem with catalogue API!")

    return response.json()


def _populate_catalog_db(db):
    # Create a collection of services
    services_collection = db["service"]
    # Populate services collection
    # TODO currently we have hardcoded 800 as maximum quantity
    services_collection.insert_many(_get_request("https://api.eosc-portal.eu/service/all?catalogue_id=eosc&quantity=800")["results"])

    # Create a collection of categories
    category_collection = db["category"]
    # Populate the category collection
    category_collection.insert_many(_get_request("https://api.eosc-portal.eu/vocabulary/byType/SUBCATEGORY"))

    # Create a collection of scientific domains
    scientific_domain_collection = db["scientific_domain"]
    # Populate scientific domain collection
    scientific_domain_collection.insert_many(_get_request("https://api.eosc-portal.eu/vocabulary/byType/SCIENTIFIC_SUBDOMAIN"))

    # Create a collection of target_users
    target_users_collection = db["target_user"]
    # Populate the target users collection
    target_users_collection.insert_many(_get_request("https://api.eosc-portal.eu/vocabulary/byType/TARGET_USER"))


if __name__ == '__main__':
    # Create catalog_dump database
    conn = MongoClient(form_mongo_url(
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_USERNAME'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_PASSWORD'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_HOST'],
                APP_SETTINGS["CREDENTIALS"]['RS_MONGO_PORT']
            ))
    db = conn["catalog_dump"]
    # Populate the database
    _populate_catalog_db(db)
