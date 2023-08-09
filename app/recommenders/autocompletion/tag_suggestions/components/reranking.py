from app.settings import APP_SETTINGS


def re_ranking(candidate_keywords):
    """
    Reranks the list of candidate keywords based on the
    final_score = score_weight * score + (1-score_weight) * popularity
    Args:
        candidate_keywords (DataFrame): columns=[tag, score, popularity]

    Returns: candidate_keywords reranked
    """

    # score_weight(float): The weight of the keyword's score (based on the keyword extractor) for the calculation of
    # the final score for reranking
    score_weight = APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]["TAGS"]["SCORE_WEIGHT"]

    # Calculate final_score for each tag
    candidate_keywords["final_score"] = score_weight * candidate_keywords["score"] + \
                                        (1-score_weight) * candidate_keywords["norm_popularity"]

    # Rerank the list of tags
    candidate_keywords.sort_values('final_score', ascending=False, inplace=True)

    return candidate_keywords
