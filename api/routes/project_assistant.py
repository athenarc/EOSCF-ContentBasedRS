import logging
from typing import List

from api.recommender.similar_services.project_assistant.recommendation_generation import \
    project_assistant_recommendation
from api.settings import APP_SETTINGS
from fastapi import APIRouter
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/v1')

STATIC_SHORT_EXPLANATION = ""
STATIC_EXPLANATION = ""


class RecommendationSet(BaseModel):
    panel_id: str
    recommendations: List[int]
    explanations: List[str]
    explanations_short: List[str]
    score: List[float]
    engine_version: str


class ProjectAssistantRecommendationParameters(BaseModel):
    description: str
    max_num: int = 5

    @validator('max_num')
    def recommendations_are_within_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError('Number of recommendations must be in the range of 0 to 20')
        return v

    class Config:
        schema_extra = {
            "example": {
                "description": "I want a service to visualize my data",
                "max_num": 5
            }
        }


@router.post(
    "/project_assistant/recommendation",
    response_model=RecommendationSet,
    tags=["recommendations"]
)
def get_project_assistant_recommendation(recommendation_parameters: ProjectAssistantRecommendationParameters):

    most_similar_services = project_assistant_recommendation(
        description=recommendation_parameters.description,
        max_num=recommendation_parameters.max_num
    )

    return RecommendationSet(
        panel_id="project_assistant",
        recommendations=[service["service_id"] for service in most_similar_services],
        score=[service["score"] for service in most_similar_services],
        explanations=[STATIC_EXPLANATION for _ in most_similar_services],
        explanations_short=[STATIC_SHORT_EXPLANATION for _ in most_similar_services],
        engine_version=APP_SETTINGS["BACKEND"]["VERSION_NAME"]
    )
