import copy

from app.settings import APP_SETTINGS


def _overlapping_tags(tag1, tag2):
    """
    Args:
        tag1 (str)
        tag2 (str)

    Returns (boolean): True if the tags are overlapping, False otherwise
    """

    tag1_tokens = set([token for token in tag1.split()])
    tag2_tokens = set([token for token in tag2.split()])

    return tag1_tokens.issubset(tag2_tokens) or tag2_tokens.issubset(tag1_tokens)


def tags_deduplication(tags):
    """
    Removes duplicate or overlapping tags.
    In case of overlaps, we keep the lengthier tag.
    Args:
        tags (DataFrame): a dataframe with the text and the score for each tag
    """
    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]
    tags["processed_tag"] = tags["text"]

    # Lowercase
    tags["processed_tag"] = tags["processed_tag"].apply(lambda tag: tag.lower())

    # Apply lemmatization in the processed_tags
    tags["processed_tag"] = tags["processed_tag"].apply(
        lambda tag: text_processor.lemmatization(tag))

    tags = tags.sort_values(by='score', ascending=False)
    # Remove duplicate tags (keep the tag with the highest score)
    tags = tags.drop_duplicates(subset="processed_tag", keep='first')

    # Find the overlapping tags
    overlaps = {}
    for idx, row in tags.iterrows():
        # Get all the overlapping tags with lowest or equal length with the current one
        tag_overlaps = tags[tags.apply(
            lambda tag:
            len(row["text"]) >= len(tag["text"]) and
            _overlapping_tags(row["processed_tag"], tag["processed_tag"]), axis=1)].index.values.tolist()

        # Remove the self reference
        tag_overlaps.remove(idx)

        # If there are overlapping tags
        if len(tag_overlaps):
            overlaps[idx] = tag_overlaps

    # Resolve conflicts
    overlaps_copy = copy.deepcopy(overlaps)
    for overlap_key, overlap_values in overlaps.items():
        for value in overlap_values:
            if value in overlaps.keys():
                overlaps_copy.pop(value, None)
    overlaps = overlaps_copy

    # Remove overlapping tags
    for _, overlap_values in overlaps.items():
        tags = tags.drop(overlap_values, errors='ignore')

    return tags[["text", "score"]]
