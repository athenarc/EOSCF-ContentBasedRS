import numpy as np

from app.recommenders.algorithms.keywords_retrieval.keywords_extraction import \
    keywords_extraction
from app.settings import APP_SETTINGS


def get_tag_candidates(text):
    method = APP_SETTINGS["BACKEND"]["AUTO_COMPLETION"]["TAGS"]["KEYWORD_EXTRACTION_METHOD"]

    tag_candidates = keywords_extraction(text, method=method)

    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]

    # Remove stopwords
    tag_candidates["text"] = tag_candidates["text"].apply(
        lambda tag: text_processor.remove_stopwords(tag))

    tag_candidates["text"].replace('', np.nan, inplace=True)
    tag_candidates.dropna(subset=["text"], inplace=True)

    return tag_candidates
