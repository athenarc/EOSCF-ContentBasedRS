import logging

from pymongo import MongoClient

logger = logging.getLogger(__name__)


def form_mongo_url(username, password, host, port) -> str:
    uri = f"mongodb://{username}:{password}@" if username and password else ""
    uri += f"{host}:{port}"
    return uri


class MongoDbConnector:
    def __init__(self, uri, db_name):
        self._uri = uri
        self._conn = None
        self._db_name = db_name
        self._db = None

    def get_db(self):
        return self._db

    def get_conn(self):
        return self._conn

    def connect(self):
        logger.debug('Connecting to the Mongo database...')
        self._conn = MongoClient(self._uri)
        self._db = self._conn[self._db_name]
