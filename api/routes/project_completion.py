import logging
from typing import List

from api.recommender.project_completion.recommendation_generation import \
    create_recommendation as project_completion_recommendation
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

router = APIRouter()


class Recommendation(BaseModel):
    service_id: int
    score: float


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


@router.post("/project_completion/recommendation", response_model=List[Recommendation])
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
        return [Recommendation(service_id=recommendation["service_id"], score=recommendation["score"])
                for recommendation in
                project_completion_recommendation(project_id=recommendation_parameters.project_id,
                                                  recommendations_num=recommendation_parameters.num)
                ]
    except Exception as e:
        logger.error("Failed to create recommendation: " + str(e))
        raise HTTPException(status_code=404, detail="Failed to create a recommendation: " + str(e))
