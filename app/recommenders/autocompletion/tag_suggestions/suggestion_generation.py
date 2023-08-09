import logging

from app.exceptions import MissingAttribute
from app.recommenders.autocompletion.tag_suggestions.components.filtering.filtering import \
    filtering
from app.recommenders.autocompletion.tag_suggestions.components.mapping import \
    map_with_tags_corpus
from app.recommenders.autocompletion.tag_suggestions.components.reranking import \
    re_ranking
from app.recommenders.autocompletion.tag_suggestions.components.tag_candidates import \
    get_tag_candidates
from app.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


def get_suggestions_for_tags(service_attributes, existing_values=None, max_num=3):
    """
    Returns a list of recommended tags
    Args:
        service_attributes: dict with the name and value for each filled field of a service
        existing_values: list[str], The list with the existing tags
        max_num: int, The maximum number of recommendations we want returned
    """

    text_attributes = APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]["TAGS"]["TEXT_ATTRIBUTES"]

    if not all(text_attribute in service_attributes for text_attribute in text_attributes):
        raise MissingAttribute("Resource does not have all necessary fields! Make sure that "
                               f"{text_attributes} are given!")

    # Get the text attributes of the service
    text_of_service = " ".join([attribute_value for attribute_key, attribute_value in service_attributes.items()
                                if attribute_key in text_attributes])

    candidate_tags = get_tag_candidates(text_of_service)

    candidate_tags, filtered_enumerated_fields = filtering(candidate_tags, existing_values)

    candidate_tags = map_with_tags_corpus(candidate_tags)

    candidate_tags = re_ranking(candidate_tags)

    return candidate_tags["text"].values.tolist()[:max_num], filtered_enumerated_fields
