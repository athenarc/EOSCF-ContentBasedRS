import math
from collections import Counter
from itertools import chain


def get_candidates(field_values, frequency_threshold=None):
    """
    Returns a list of values based on frequency across values sets
    @param field_values: list<list<str>>, a list with the values of a field for several services
    @return list<str>
    """
    if len(field_values) == 0:
        return []

    if frequency_threshold is None:
        frequency_threshold = 0

    # Calculate the appearances of each value
    values_count = dict(Counter(chain(*field_values)))

    # Filter values
    counts_threshold = math.ceil(frequency_threshold * len(field_values))
    filtered_values = dict(filter(lambda elem: elem[1] >= counts_threshold, values_count.items())).keys()

    return list(filtered_values)
