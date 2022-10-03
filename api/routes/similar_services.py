import logging
from typing import List

from api.recommender.similar_services.recommendation_generation import \
    IdNotExists
from api.recommender.similar_services.recommendation_generation import \
    create_recommendation as similar_services_recommendation
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

router = APIRouter()


class Recommendation(BaseModel):
    service_id: int
    score: float


class SimilarServicesRecommendationParameters(BaseModel):
    user_id: int = None
    service_id: int
    num: int = 5

    @validator('user_id')
    def id_is_positive_or_none(cls, v):
        if v is not None and v < 0:
            raise ValueError('Ids must be positive integers')
        return v

    @validator('service_id')
    def id_is_positive(cls, v):
        if v < 0:
            raise ValueError('Ids must be positive integers')
        return v

    @validator('num')
    def recommendations_are_within_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError('Number of recommendations must be in the range of 0 to 20')
        return v


@router.post(
    "/similar_services/recommendation",
    response_model=List[Recommendation],
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
        return [Recommendation(service_id=recommendation["service_id"], score=recommendation["score"])
                for recommendation in
                similar_services_recommendation(viewed_resource_id=str(recommendation_parameters.service_id),
                                                recommendations_num=recommendation_parameters.num,
                                                user_id=recommendation_parameters.user_id)
                ]

    except IdNotExists as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
