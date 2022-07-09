from typing import List

from api.recommender.similar_services.initialization.metadata_structure import \
    METADATA_STRUCTURES
from api.recommender.similar_services.initialization.text_structure import \
    TEXT_STRUCTURES
from api.recommender.similar_services.recommendation_generation import \
    create_recommendation as similar_services_recommendation
from api.settings import APP_SETTINGS
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Recommendation(BaseModel):
    service_ids: List[int]


class SimilarServicesRecommendationParameters(BaseModel):
    user_id: int = None
    service_id: int
    num: int = 5


@router.post(
    "/similar_services/recommendation",
    response_model=Recommendation,
)
def get_similar_services_recommendation(recommendation_parameters: SimilarServicesRecommendationParameters):
    """
    **Suggest a similar service**

    Based on the service given as input, we recommend similar services utilizing both textual and metadata
    attributes.

    - **user_id**: the id of the user (as it was given in the marketplace)
    - **service_id**: the id of the service currently viewed by the user
    - **num**: number of recommendations we want returned
    """
    return Recommendation(service_ids=
                          similar_services_recommendation(viewed_resource_id=str(recommendation_parameters.service_id),
                                                          recommendations_num=recommendation_parameters.num,
                                                          user_id=recommendation_parameters.user_id)
                          )


@router.get(
    "/update",
    summary="Update all data structures",
    description="The data structures created (such as embeddings) need updating every x hours."
)
def update():
    # update similar services
    sim_serv_settings = APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]
    TEXT_STRUCTURES.update(sim_serv_settings["EMBEDDINGS_STORAGE_PATH"] + "metadata_embeddings.parquet",
                           sim_serv_settings["SIMILARITIES_STORAGE_PATH"] + "metadata_similarities.parquet")
    METADATA_STRUCTURES.update(sim_serv_settings["EMBEDDINGS_STORAGE_PATH"] + "text_embeddings.parquet",
                               sim_serv_settings["SIMILARITIES_STORAGE_PATH"] + "text_similarities.parquet")
