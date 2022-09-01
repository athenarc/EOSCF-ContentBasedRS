import pickle
import zlib

import redis
from api.settings import APP_SETTINGS

redis_server = redis.Redis(
    host=APP_SETTINGS["CREDENTIALS"]['INTERNAL_REDIS_HOST'],
    port=APP_SETTINGS["CREDENTIALS"]['INTERNAL_REDIS_PORT'],
    password=APP_SETTINGS["CREDENTIALS"]['INTERNAL_REDIS_PASSWORD']
)


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
