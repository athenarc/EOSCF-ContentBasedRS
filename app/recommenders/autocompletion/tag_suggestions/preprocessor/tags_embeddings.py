import gensim.downloader as api
import re
import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_word2vec_embeddings():
    """
    Returns:
        word_embeddings (dict): dictionary that includes words and their embeddings
    """
    word2vec_model = api.load('glove-wiki-gigaword-300')
    return word2vec_model

word2vec_embeddings = get_word2vec_embeddings()

def create_tag_embedding(tag):
    """
    Returns the embedding of the tag based on word2vec. None if the tag is oov(out-of-vocabulary)
    Args:
        tag (str): The text of the tag
    """
    words = re.split(r" |-", tag)
    embeddings = []
    for word in words:
        if word == "":
            continue
        word = word.lower()
        if word not in word2vec_embeddings:
            return None
        embeddings.append(word2vec_embeddings[word])

    return np.average(embeddings, axis=0)


def create_tag_embeddings(tags):
    """
    Stores and returns a tag embeddings structure (using word2vec) and a list with all the out-of-vocabulary tags.
    Args:
        tags (DataFrame): columns=[text, ...]
    """

    logger.debug("Creating tag embeddings...")

    tags_embeddings = []
    for _, tag in tags.iterrows():
        tags_embeddings.append(create_tag_embedding(tag["text"]))
    tags["embedding"] = tags_embeddings

    return tags
