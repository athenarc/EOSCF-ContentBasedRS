import datetime
import logging
from typing import Optional

from app.databases.utils.mongo_connector import (MongoDbConnector,
                                                 form_mongo_url)
from app.settings import APP_SETTINGS
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class ContentBasedRecsMongoDB:
    def __init__(self):
        self.mongo_connector = MongoDbConnector(
            uri=form_mongo_url(
                APP_SETTINGS["CREDENTIALS"]['CONTENT_BASED_RS_MONGO_USERNAME'],
                APP_SETTINGS["CREDENTIALS"]['CONTENT_BASED_RS_MONGO_PASSWORD'],
                APP_SETTINGS["CREDENTIALS"]['CONTENT_BASED_RS_MONGO_HOST'],
                APP_SETTINGS["CREDENTIALS"]['CONTENT_BASED_RS_MONGO_PORT']
            ),
            db_name=APP_SETTINGS["CREDENTIALS"]['CONTENT_BASED_RS_MONGO_DATABASE']
        )
        self.mongo_connector.connect()

    def check_health(self) -> Optional[str]:
        # Check that the database is up
        try:
            db_names = self.mongo_connector.get_conn().list_database_names()
        except ServerSelectionTimeoutError:
            error = "Could not establish connection with content based RS mongo"
            logger.error(error)
            return error

        if APP_SETTINGS["CREDENTIALS"]['CONTENT_BASED_RS_MONGO_DATABASE'] in db_names:
            return None
        else:
            error = f"Content based RS target database " \
                    f"{APP_SETTINGS['CREDENTIALS']['CONTENT_BASED_RS_MONGO_DATABASE']} does not exist"
            logger.error(error)
            return error

    def save_recommendation_set(self, recommendation_set, user_id, service_id, history_service_ids):
        document = {
            "date": datetime.datetime.utcnow(),
            "version": APP_SETTINGS["BACKEND"]["VERSION_NAME"],
            "service_id": service_id,
            "recommendation": recommendation_set,
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
                "sbert_model": APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SBERT"]["MODEL"]._model_card_vars["name"]
            },
            "project_completion": {
                "min_support": APP_SETTINGS["BACKEND"]["PROJECT_COMPLETION"]["MIN_SUPPORT"],
                "min_confidence": APP_SETTINGS["BACKEND"]["PROJECT_COMPLETION"]["MIN_CONFIDENCE"]
            }

        }

        # Update the version if it exists or create a new version document
        self.mongo_connector.get_db()["version"].update_one({"name": version["name"]}, {"$set": version}, upsert=True)

        logger.debug("Recommender version was successfully saved!")
