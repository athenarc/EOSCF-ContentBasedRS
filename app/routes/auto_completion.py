import logging
from typing import List

from app.exceptions import MissingAttribute, MissingStructure
from app.recommender.similar_services.field_suggestion.evaluation.evaluation import \
    evaluation
from app.recommender.similar_services.field_suggestion.suggestion_generation import \
    get_auto_complete_suggestions
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/v1')


class Request(BaseModel):

    new_service: dict

    # Fields to suggest options
    fields_to_suggest: List[str]

    # The maximum suggestions per field
    maximum_suggestions: int

    class Config:
        schema_extra = {
            "example": {
                "new_service": {
                    "name": "Name of the service...",
                    "description": "Description of the added service..."
                },
                "fields_to_suggest": ["categories", "target_users", "scientific_domains"],
                "maximum_suggestions": 3
            }
        }


class FieldSuggestions(BaseModel):
    field_name: str
    suggestions: List[str]


@router.post(
    "/auto_completion/suggest",
    response_model=List[FieldSuggestions],
    tags=["fields auto-completion"]
)
def auto_completion_suggestions(request: Request):
    """
    **Create auto-complete suggestions for the requested fields**

    Based on the new service's filled fields given as input, we recommend auto-complete suggestions for the requested
    fields utilizing the fields of similar services.

    - **new_service**: the filled fields of the new partial created service
    - **fields_to_suggest**: the fields for which suggestion will be generated
    - **maximum_suggestions**: the maximum number of suggestions per field

    **Returns** a list with the name and the suggestions for every requested field
    """
    try:
        return [FieldSuggestions(field_name=field, suggestions=suggestions)
                for field, suggestions in get_auto_complete_suggestions(request.new_service, request.fields_to_suggest,
                                                          request.maximum_suggestions).items()]
    except (MissingStructure, MissingAttribute) as e:
        logger.error((str(e)))
        raise HTTPException(status_code=404, detail=str(e))


class FieldCompletionEvaluation(BaseModel):
    field: str
    results: dict


@router.post(
    "/auto_completion/evaluate",
    response_model=List[FieldCompletionEvaluation],
    tags=["fields auto-completion"]
)
def evaluate_auto_completion():
    try:
        return [FieldCompletionEvaluation(field=field, results=results)
                for field, results in evaluation().items()]
    except MissingStructure as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
