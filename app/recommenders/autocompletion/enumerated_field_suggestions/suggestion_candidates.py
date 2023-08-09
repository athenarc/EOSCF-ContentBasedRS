import math
from collections import Counter
from itertools import chain


def get_candidates(field_values, frequency_threshold=None, existing_values=None):
    """
    Returns a list of values based on frequency across values sets
    Args:
        field_values: list<list>, a list with all values of a field of the most similar services
        frequency_threshold: float, the required frequency threshold for each candidate value
        existing_values: list, the existing values for the field

    Returns: list of candidate values

    """
    if len(field_values) == 0:
        return []

    if frequency_threshold is None:
        frequency_threshold = 0

    # Calculate the appearances of each value
    values_count = dict(Counter(chain(*field_values)))

    # Filter values based on
    counts_threshold = math.ceil(frequency_threshold * len(field_values))
    filtered_values = list(dict(filter(lambda elem: elem[1] >= counts_threshold, values_count.items())).keys())

    # If there are already some values in the field, filter them
    if existing_values is not None:
        filtered_values = list(set(filtered_values).difference(set(existing_values)))

    return filtered_values
