import datetime
import logging
import random

import numpy as np
from api.databases.mongo import RSMongoDB
from api.databases.postgres import MPPostgresDb
from api.evaluation.synthetic_recommendations_db import UserActionsDB
from api.recommender.similar_services.recommendation_generation import \
    create_recommendation

logger = logging.getLogger(__name__)


def get_service_slug(service_id):

    db = MPPostgresDb()

    service = db.get_services(attributes=["slug"], conditions=f"id = {int(service_id)}")

    return service.iloc[0]["slug"] if service.shape[0] > 0 else None


def create_synthetic_recommendations(num):

    db = RSMongoDB()
    user_actions_db = UserActionsDB()

    # Choose num random users
    users = db.get_users(attributes="_id")
    selected_user_ids = np.random.choice(users, num, replace=False)

    # Choose num random services
    services = db.get_services()
    selected_service_ids = np.random.choice(services["service_id"].values, num, replace=False)

    # Create a recommendation
    for service_id, user_id in zip(selected_service_ids, selected_user_ids):

        service_slug = get_service_slug(service_id)

        # If the service does not exist in postgres
        if service_slug is None:
            continue

        service_page_id = "/services/" + service_slug

        user_actions = [{
            "user": int(user_id),
            "unique_id": None,
            "timestamp": datetime.datetime.utcnow(),
            "source": {
                "_cls": "Source",
                "visit_id": None,
                "page_id": "/services",
                "root": {
                    "type": "other"
                }
            },
            "target": {
                "_cls": "Target",
                "visit_id": None,
                "page_id": service_page_id,
            },
            "action": {
                "type": "browser action",
                "text": "",
                "order": False
            },
            "processed": True
        }]

        # Create synthetic user action from home page to service page

        # Create synthetic recommendation
        recommendation = create_recommendation(str(service_id), recommendations_num=5, user_id=user_id)

        # Create synthetic user action from service to recommended service
        if random.randint(0, 100) > 15:
            # choose a recommendation to browse
            chosen_recommendation = random.choice(list(map(lambda x: int(x["service_id"]), recommendation)))
            chosen_service_slug = get_service_slug(chosen_recommendation)
            # If the service exists in the postgres database, and we can find its slug
            if chosen_service_slug is not None:
                # create corresponding user action
                user_actions.append({
                    "user": int(user_id),
                    "unique_id": None,
                    "timestamp": datetime.datetime.utcnow(),
                    "source": {
                        "_cls": "Source",
                        "visit_id": None,
                        "page_id": service_page_id,
                        "root": {
                            "type": "recommendation_panel",
                            "panel_id": "",
                            "service_id": int(service_id)
                        }
                    },
                    "target": {
                        "_cls": "Target",
                        "visit_id": None,
                        "page_id": "/services/" + chosen_service_slug,
                    },
                    "action": {
                        "type": "browser action",
                        "text": "",
                        "order": False
                    },
                    "processed": True
                })

        # Store user actions
        user_actions_db.save_user_actions(user_actions)
