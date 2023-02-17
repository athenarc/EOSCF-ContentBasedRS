import logging
import pickle
import zlib
from typing import Optional

import redis
from app.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


redis_server = redis.Redis(
    host=APP_SETTINGS["CREDENTIALS"]['INTERNAL_REDIS_HOST'],
    port=APP_SETTINGS["CREDENTIALS"]['INTERNAL_REDIS_PORT'],
    password=APP_SETTINGS["CREDENTIALS"]['INTERNAL_REDIS_PASSWORD']
)


def check_health() -> Optional[str]:
    # Check that redis is up
    try:
        redis_server.ping()
    except redis.ConnectionError:
        error = "Could not establish connection with redis"
        logger.error(error)
        return error

    return None


def store_object(df, structure_type):
    df_compressed = zlib.compress(pickle.dumps(df))
    res = redis_server.set(structure_type, df_compressed)

    if not res:
        raise redis.DataError(f"Failed to store dataframe of {structure_type}")


def get_object(structure_type):
    data = redis_server.get(structure_type)
    return pickle.loads(zlib.decompress(data))


def check_key_existence(structure_type):
    return redis_server.exists(structure_type)


def delete_object(structure_type):
    redis_server.delete(structure_type)
