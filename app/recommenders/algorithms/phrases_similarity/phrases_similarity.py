import pandas as pd
from polyleven import levenshtein
from similarity.normalized_levenshtein import NormalizedLevenshtein

normalized_levenshtein = NormalizedLevenshtein()


def phrases_similarity(phrase, compared_phrases):
    """
    Calculate the similarity with every compared phrase
    Args:
        phrase: str
        compared_phrases: list[str]

    Returns: Series
    """
    similarities = []
    # Calculate the similarity with every compared phrase
    for compared_phrase in compared_phrases:
        similarities.append(phrase_similarity(phrase, compared_phrase))

    return pd.Series(similarities)


def phrase_similarity(phrase, compared_phrase):
    max_len = max(len(phrase), len(compared_phrase))
    return 1 - (levenshtein(phrase, compared_phrase) / max_len)
