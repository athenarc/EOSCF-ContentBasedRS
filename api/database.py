import pandas as pd
import logging
import psycopg2

logger = logging.getLogger(__name__)


class PostgresDb:
    def __init__(self, settings):
        self._settings = settings
        self._conn = None

    def connect(self):
        try:
            logger.info('Connecting to the PostgreSQL database...')
            self._conn = psycopg2.connect(
                host=self._settings['HOST'],
                database=self._settings['DATABASE'],
                user=self._settings['USER'],
                password=self._settings['PASSWORD'])

        except Exception as error:
            logger.error(error)

    def close_connection(self):
        if not self._conn.closed:
            logger.info('Closing connection with the PostgreSQL database...')
            self._conn.close()

    def execute(self, query, params):
        try:
            cur = self._conn.cursor()
            cur.execute(query, params)
            res = cur.fetchall()
            cur.close()

            return res
        except Exception as error:
            logger.error(error)

    def get_services(self, attributes=None, conditions=None):

        if attributes is None:
            attributes = []

        select_attributes = ", ".join(["id as service_id"] + attributes)
        query = f"""
            SELECT {select_attributes}
            FROM services
        """

        if conditions is not None:
            query += f"""WHERE {conditions}"""

        results = pd.DataFrame(self.execute(query, ()), columns=["service_id"] + attributes)

        return results

    def get_services_providers(self):
        attributes = ['service_id', 'provider_name']

        query = f"""
            SELECT service_id, providers.name as provider_name
            FROM services, service_providers, providers
            WHERE services.id = service_providers.service_id and providers.id = service_providers.provider_id
        """
        results = (pd.DataFrame(self.execute(query, ()), columns=attributes).groupby("service_id")["provider_name"].agg(
            list)).reset_index(name="provider_names")

        return results

    def get_services_scientific_domains(self):
        query = f"""
            SELECT service_id, scientific_domain_id
            FROM service_scientific_domains
        """
        results = (
            pd.DataFrame(self.execute(query, ()), columns=['service_id', 'scientific_domain_id']).groupby("service_id")["scientific_domain_id"].agg(
                list)).reset_index(name="scientific_domains")

        return results

    def get_services_target_users(self):
        attributes = ['service_id', 'target_user_id']

        query = f"""
            SELECT service_id, target_user_id
            FROM service_target_users
        """
        results = (
            pd.DataFrame(self.execute(query, ()), columns=attributes).groupby("service_id")["target_user_id"].agg(
                list)).reset_index(name="target_users")

        return results

    def get_services_relationships(self):
        query = f"""
            SELECT source_id as service_id, target_id as related_service_id
            FROM service_relationships
        """
        results = (
            pd.DataFrame(self.execute(query, ()), columns=['service_id', 'related_service_id']).groupby("service_id")["related_service_id"].agg(
                list)).reset_index(name="related_service")

        return results

    def get_services_categories(self):
        query = f"""
            SELECT service_id, category_id
            FROM categorizations
        """

        results = (
            pd.DataFrame(self.execute(query, ()), columns=['service_id', 'category_id']).groupby("service_id")["category_id"].agg(
                list)).reset_index(name="categories")

        return results

    def get_services_tags(self):
        query = f"""
            SELECT tagger_id as service_id, tag_id
            FROM taggings
            WHERE tagger_type = "Service"
        """

        results = (
            pd.DataFrame(self.execute(query, ()), columns=['service_id', 'tag_id']).groupby("service_id")["tag_id"].agg(
                list)).reset_index(name="tags")

        return results

    def get_scientific_domains(self, conditions=None):

        query = f"SELECT id FROM scientific_domains"

        if conditions is not None:
            query += f"WHERE {conditions}"

        return [r[0] for r in self.execute(query, ())]

    def get_categories(self, conditions=None):
        query = f"SELECT id FROM categories"

        if conditions is not None:
            query += f"WHERE {conditions}"

        return [r[0] for r in self.execute(query, ())]

    def get_target_users(self, conditions=None):
        query = f"SELECT id FROM target_users"

        if conditions is not None:
            query += f"WHERE {conditions}"

        return [r[0] for r in self.execute(query, ())]

    def get_user_services(self, user_id):
        query = f"SELECT service_id FROM user_services WHERE user_id = {user_id}"
        return [r[0] for r in self.execute(query, ())]
