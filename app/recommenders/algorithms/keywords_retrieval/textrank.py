import pandas as pd
from app.settings import APP_SETTINGS


def textrank(text):
    """
    Returns the keywords extracted from the text with their scores
    Args:
        text: str
    Returns: list[tuple(str, float)]

    """
    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]

    keywords = {"keyword": [], "score": [], "count": []}
    for phrase in text_processor.textrank(text):
        keywords["keyword"].append(phrase.text)
        keywords["score"].append(phrase.rank)
        keywords["count"].append(phrase.count)

    keywords_df = pd.DataFrame(keywords)
    return keywords_df[["keyword", "score"]]
