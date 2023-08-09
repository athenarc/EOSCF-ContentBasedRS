from app.databases.content_based_rec_db import ContentBasedRecsMongoDB
from app.recommenders.similar_services.components.get_similar_services import \
    User


def store_recommendation(recommendation_set, viewed_service_id, user_id):
    user = User(user_id)
    purchases = user.get_purchases()

    content_based_recs_db = ContentBasedRecsMongoDB()
    content_based_recs_db.save_recommendation_set(recommendation_set=recommendation_set, service_id=viewed_service_id,
                                                  user_id=user_id, history_service_ids=purchases)
