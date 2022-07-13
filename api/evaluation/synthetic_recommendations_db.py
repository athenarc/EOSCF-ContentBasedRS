import logging

from api.databases.mongo import MongoDbConnector
from api.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


class UserActionsDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_URI'],
                                                APP_SETTINGS["CREDENTIALS"]['INTERNAL_MONGO_DATABASE'])
        self.mongo_connector.connect()

    def save_user_actions(self, user_actions):
        self.mongo_connector.get_db()["user_actions"].insert_many(user_actions)
