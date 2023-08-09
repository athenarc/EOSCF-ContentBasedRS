import json

import pandas as pd
from app.databases.registry.registry_selector import get_registry
from app.recommenders.autocompletion.tag_suggestions.components.filtering.filtering import \
    filtering
from app.recommenders.autocompletion.tag_suggestions.components.tag_candidates import \
    get_tag_candidates
from app.settings import APP_SETTINGS
from tqdm import tqdm


def initialize_tag_corpus(max_tags_per_service=4):
    """
    Returns and save to redis an initial tag corpus based on the services existing in the registry.
    Args:
        max_tags_per_service (int): the maximum number of tags used from each service

    Returns (DataFrame): DataFrame(columns=[tag, count]) with the tags and their number appearances
    """

    db = get_registry()

    text_attributes = APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]["TAGS"]["TEXT_ATTRIBUTES"]
    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]

    # Get all services
    services = db.get_services(attributes=["description", "tagline"])

    # Extract suggested tags from all services
    suggested_tags = []
    for _, service in tqdm(services.iterrows(), desc="Tag corpus initialization..."):
        # Get the text attributes of the service
        text_of_service = text_processor.cleaning(
            " ".join([attribute_value for attribute_key, attribute_value in service.items()
                      if attribute_key in text_attributes]))

        service_suggested_tags = get_tag_candidates(text_of_service)
        service_suggested_tags = filtering(service_suggested_tags)

        suggested_tags.extend(service_suggested_tags["keyword"].values.tolist()[:max_tags_per_service])

    # Apply text preprocess to all suggested tags (e.g., lowercase)
    suggested_tags = text_processor.normalization(suggested_tags)

    # Remove duplicates and store count
    suggested_tags = pd.DataFrame({"tags": suggested_tags})
    count_per_tag = suggested_tags["tags"].value_counts()
    suggested_tags = pd.DataFrame({"tag": count_per_tag.keys(), "count": count_per_tag.values})

    # TODO save to redis

    return suggested_tags


if __name__ == '__main__':
    initialize_tag_corpus(max_tags_per_service=10)
