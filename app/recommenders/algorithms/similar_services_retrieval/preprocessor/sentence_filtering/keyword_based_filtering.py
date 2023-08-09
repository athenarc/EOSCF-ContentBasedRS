from app.recommenders.algorithms.keywords_retrieval.keywords_extraction import \
    keywords_extraction


def check_keyword_existence(keywords, sentence):
    for keyword in keywords:
        if keyword in sentence:
            return True
    return False


def sentence_filtering_from_keywords(sentences):
    keywords = keywords_extraction(' '.join(sentences))

    top_n = 4
    selected_keywords = keywords["keyword"].values.tolist()[:top_n]

    selected_sentences = [sentence for sentence in sentences
                          if check_keyword_existence(selected_keywords, sentence)]

    # removed_sentences = [sentence for sentence in sentences
    #                      if not check_keyword_existence(selected_keywords, sentence)]

    # print("#" * 120)
    # print("Selected sentences")
    # for sent in selected_sentences:
    #     print(sent)
    # print("-" * 120)
    # print("Removed sentences")
    # for sent in removed_sentences:
    #     print(sent)

    return selected_sentences
