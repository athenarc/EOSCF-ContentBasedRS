import logging
from typing import Any, List
from datetime import datetime


from app.exceptions import IdNotExists
from app.recommenders.similar_services.recommendation_set_generation import \
    create_recommendation_set as similar_services_recommendation
from app.settings import APP_SETTINGS
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/v1')

STATIC_SHORT_EXPLANATION = "Similar metadata and text to the service you are viewing"
STATIC_EXPLANATION = "Based on the metadata and the text attributes we retrieve the services that are most " \
                     "similar to the one you are currently viewing."


class RecommendationSet(BaseModel):
    panel_id: str
    recommendations: List[int]
    explanations: List[str]
    explanations_short: List[str]
    score: List[float]
    engine_version: str


class SimilarServicesRecommendationParameters(BaseModel):
    user_id: int = None
    service_id: Any
    num: int = 5

    # The fields below are not used in the recommendation algorithm 
    # but are used for logging purposes
    unique_id: str = None
    aai_uid: str = None
    timestamp: datetime = None

    @validator('user_id')
    def id_is_positive_or_none(cls, v):
        if v is not None and v < 0:
            raise ValueError('User ids must be positive integers')
        return v

    @validator('num')
    def recommendations_are_within_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError('Number of recommendations must be in the range of 0 to 20')
        return v

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "service_id": 62,
                "num": 5,
                "unique_id": "unique_id",
                "aai_uid": "aai_uid",
                "timestamp": "2020-03-04T09:00:00.000Z"
            }
        }


@router.post(
    "/similar_services/recommendation",
    response_model=RecommendationSet,
    tags=["recommendations"]
)
def get_similar_services_recommendation(recommendation_parameters: SimilarServicesRecommendationParameters):
    """
    **Suggest a similar service**

    Based on the service given as input, we recommend similar services utilizing both textual and metadata
    attributes.

    - **user_id**: the id of the user (as it was given in the marketplace)
    - **service_id**: the id of the service currently viewed by the user
    - **num**: number of recommendations we want returned

    **Returns** a list of dicts where service_id is the id of the recommended service and score is the similarity with
    the currently viewed service.
    """
    try:
        most_similar_services = similar_services_recommendation(
            viewed_service_id=recommendation_parameters.service_id,
            recommendations_num=recommendation_parameters.num,
            user_id=recommendation_parameters.user_id,
            do_rerank=False
        )

        return RecommendationSet(
            panel_id="similar_services",
            recommendations=[service['service_id'] for service in most_similar_services],
            scores=[service['score'] for service in most_similar_services],
            explanations=[STATIC_EXPLANATION for _ in most_similar_services],
            explanations_short=[STATIC_SHORT_EXPLANATION for _ in most_similar_services],
            engine_version=APP_SETTINGS["BACKEND"]["VERSION_NAME"]
        )
    except IdNotExists as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
