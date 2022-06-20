from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from api.recommender.recommendation_generation import create_recommendation, test_recommendation

router = APIRouter()


class Recommendation(BaseModel):
    service_ids: List[int]


class RecommendationParameters(BaseModel):
    user_id: int = None
    service_id: int
    num: int = 5
    view_weight: float = 0.5
    metadata_weight: float = 0.5


class TestRecommendationParameters(BaseModel):
    service_id: int
    purchase_ids: list = []
    num: int = 5
    view_weight: float = 0.5
    metadata_weight: float = 0.5


@router.post("/recommendation", response_model=Recommendation)
def get_recommendation(recommendation_parameters: RecommendationParameters):
    return Recommendation(service_ids=
                          create_recommendation(viewed_resource_id=str(recommendation_parameters.service_id),
                                                recommendations_num=recommendation_parameters.num,
                                                user_id=recommendation_parameters.user_id,
                                                viewed_weight=recommendation_parameters.view_weight,
                                                metadata_weight=recommendation_parameters.metadata_weight))


@router.post("/rs_evaluation/recommendation", response_model=Recommendation)
def get_recommendation(recommendation_parameters: TestRecommendationParameters):
    return Recommendation(service_ids=
                          test_recommendation(viewed_resource_id=str(recommendation_parameters.service_id),
                                              purchases=list(map(str, recommendation_parameters.purchase_ids)),
                                              recommendations_num=recommendation_parameters.num,
                                              viewed_weight=recommendation_parameters.view_weight,
                                              metadata_weight=recommendation_parameters.metadata_weight))
