from app.exceptions import MethodDoesNotExist
from app.recommenders.algorithms.keywords_retrieval.textrank import textrank


def keywords_extraction(text, method="textrank"):
    if method == "textrank":
        keywords = textrank(text)
    else:
        raise MethodDoesNotExist(f"Keyword extraction method {method} is unknown.")

    keywords.rename(columns={"keyword": "text"}, inplace=True)
    return keywords.sort_values(by='score', ascending=False)
