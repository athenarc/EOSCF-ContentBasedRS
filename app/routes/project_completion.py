import logging
from typing import List

from app.recommender.project_completion.recommendation_generation import \
    create_recommendation as project_completion_recommendation
from app.settings import APP_SETTINGS
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/v1')

STATIC_SHORT_EXPLANATION = "Similar projects frequently added this service."
STATIC_EXPLANATION = "This service was added to other projects that had part of the services that you have added to " \
                     "this project."


class RecommendationSet(BaseModel):
    panel_id: str
    recommendations: List[int]
    explanations: List[str]
    explanations_short: List[str]
    score: List[float]
    engine_version: str


class ProjectCompletionRecommendationParameters(BaseModel):
    project_id: int
    num: int = 5

    @validator('project_id')
    def id_is_positive(cls, v):
        if v < 0:
            raise ValueError('Ids must be positive integers')
        return v

    @validator('num')
    def recommendations_are_within_range(cls, v):
        if v < 0 or v > 20:
            raise ValueError('Number of recommendations must be in the range of 1 to 20')
        return v

    class Config:
        schema_extra = {
            "example": {
                "project_id": 1,
                "num": 5
            }
        }


@router.post("/project_completion/recommendation", response_model=RecommendationSet, tags=["recommendations"])
def get_project_completion_recommendation(recommendation_parameters: ProjectCompletionRecommendationParameters):
    """
    **Suggest a completion for the project**

    Based on the project given as input, we recommend services that are frequently combined with the ones existing in
    the project.

    - **project_id**: the id of the project currently viewed by the user
    - **num**: number of recommendations we want returned

    **Returns** a list of dicts where service_id is the id of the recommended service and score is the support from the
    frequent item sets.
    """
    try:
        services_of_similar_projects = project_completion_recommendation(
            project_id=recommendation_parameters.project_id,
            recommendations_num=recommendation_parameters.num)

        return RecommendationSet(
            panel_id="project_completion",
            recommendations=[service['service_id'] for service in services_of_similar_projects],
            score=[service['score'] for service in services_of_similar_projects],
            explanations=[STATIC_EXPLANATION for _ in services_of_similar_projects],
            explanations_short=[STATIC_SHORT_EXPLANATION for _ in services_of_similar_projects],
            engine_version=APP_SETTINGS["BACKEND"]["VERSION_NAME"]
        )
    except Exception as e:
        logger.error("Failed to create recommendation: " + str(e))
        raise HTTPException(status_code=404, detail="Failed to create a recommendation: " + str(e))
