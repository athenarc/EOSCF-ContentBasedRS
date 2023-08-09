import logging
import time

from app.databases import redis_db
from app.databases.registry.registry_selector import get_registry
from app.recommenders.algorithms.phrases_similarity.phrases_similarity import (
    phrase_similarity, phrases_similarity)

logger = logging.getLogger(__name__)


def enumerated_fields_filtering(tags, sim_threshold):
    """
        Filter out the values from the following fields:
            - scientific domains, scientific subdomains
            - supercategories, categories, subcategories
            - target users
        Args:
            tags: DataFrame(columns=[keywords, score])
            sim_threshold: float ∈ [0,1], the similarity value threshold for which 2 phrases can be considered similar

        Returns: DataFrame(columns=[keywords, score]), List(str)
        """
    if len(tags) == 0:
        return tags

    # print("#"*100)
    # We are keeping the subvalues so as we can inject them in subcategories, scientific subdomains suggestions
    # We do not keep the upper values (i.e. supercategories, categories, scientific domains)
    tags, filtered_out_subvalues = filter_enumerated_fields_sub_values(tags, sim_threshold)
    tags = filter_enumerated_fields_upper_values(tags, sim_threshold)

    return tags, filtered_out_subvalues


def get_enumerated_field(field_name):
    if redis_db.check_key_existence(field_name):
        return redis_db.get_object(field_name)

    db = get_registry()

    if field_name == "SUBCATEGORIES":
        ret_field = db.get_subcategories_id_and_name()
    elif field_name == "SCIENTIFIC_SUBDOMAINS":
        ret_field = db.get_scientific_subdomains_id_and_name()
    elif field_name == "TARGET_USERS":
        ret_field = db.get_target_users_id_and_name()
    elif field_name == "UPPER_CATEGORIES":
        ret_field = db.get_upper_categories_id_and_name()
    elif field_name == "UPPER_SCIENTIFIC_DOMAINS":
        ret_field = db.get_scientific_upper_domains_id_and_name()
    else:
        raise ValueError(f"Field {field_name} not supported")

    redis_db.store_object(ret_field, field_name, expire_seconds=60*60)

    return ret_field


def filter_enumerated_fields_sub_values(tags, sim_threshold):
    """
    Filter out the values from the following fields:
        - scientific subdomains
        - subcategories
        - target users
    Args:
        tags: DataFrame(columns=[text, score])
        sim_threshold: float ∈ [0,1], the similarity value threshold for which 2 phrases can be considered similar

    Returns: DataFrame(columns=[text, score]), List(str)
    """
    start_time = time.time()

    # Filter values based on similarity threshold
    enumerated_field_values = {
        "scientific_domains": get_enumerated_field("SCIENTIFIC_SUBDOMAINS"),
        "categories": get_enumerated_field("SUBCATEGORIES"),
        "target_users": get_enumerated_field("TARGET_USERS")
    }

    filtered_out_values_per_field = {}

    tags = tags.reset_index()  # We need to reset to access the index sequentially later
    selected_tags = [True] * len(tags)

    for field_category, field_values in enumerated_field_values.items():
        filtered_out_values_per_field[field_category] = \
            find_enumerated_field_sub_values(tags, field_values, sim_threshold, selected_tags)

    tags = tags[selected_tags]  # Filter out the tags that were matched with enumerated values

    # Filter out conflicts and flatten
    filtered_out_values_no_conflicts = {}
    for domain, values in filtered_out_values_per_field.items():
        filtered_out_values_no_conflicts[domain] = [value[0] for value in values if len(value) == 1]

    logger.debug(f"Filter metadata values {time.time() - start_time} sec")

    start_time = time.time()

    logger.debug(f"Filter services names {time.time() - start_time} sec")

    return tags, filtered_out_values_no_conflicts


def find_enumerated_field_sub_values(tags, field_values, sim_threshold, selected_tags):
    filtered_out_values = []

    for ind, row in tags.iterrows():
        matched_fields = []
        for field_id, field_name in field_values:
            if phrase_similarity(field_name, row["text"]) > sim_threshold:
                matched_fields.append(field_id)
                # print(f"{row['text']} - {field_id} - {field_name}")
                selected_tags[ind] = False

        if len(matched_fields) > 0:
            filtered_out_values.append(matched_fields)

    return filtered_out_values


def filter_enumerated_fields_upper_values(tags, sim_threshold):
    """
    Filter out the values from the following fields:
        - scientific domains
        - supercategories, categories

    We make a separation between the upper-values and the sub-values since we do not need to keep the ids of the latter
    leading to sped up filtering.
    Args:
        tags: DataFrame(columns=[text, score])
        sim_threshold: float ∈ [0,1], the similarity value threshold for which 2 phrases can be considered similar

    Returns: DataFrame(columns=[text, score])
    """
    scientific_upper_domains = get_enumerated_field("UPPER_SCIENTIFIC_DOMAINS")
    upper_categories = get_enumerated_field("UPPER_CATEGORIES")

    upper_values_names = [value[1] for value in scientific_upper_domains + upper_categories]

    tags = tags[~tags.apply(
        lambda tag:
        phrases_similarity(tag["text"], upper_values_names)
        .apply(lambda sim: sim > sim_threshold).any()
        , axis=1)]

    return tags
