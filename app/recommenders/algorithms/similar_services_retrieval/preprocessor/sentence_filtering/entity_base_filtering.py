from app.settings import APP_SETTINGS

ACCEPTED_ENTITIES = {'PERSON', 'FAC', 'ORG', 'PRODUCT', 'EVENT', 'CARDINAL', 'ORDINAL', 'QUANTITY'}


def check_entity_existence(entities, sentence):
    for entity in entities:
        if entity in sentence:
            return True
    return False


def sentence_filtering_from_entities(sentences):
    text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]
    entities = text_processor.ner(' '.join(sentences))

    accepted_entities_text = {entity.text for entity in entities if entity.label_ in ACCEPTED_ENTITIES}

    selected_sentences = [sentence for sentence in sentences
                          if check_entity_existence(accepted_entities_text, sentence)]

    # removed_sentences = [sentence for sentence in sentences
    #                      if not check_entity_existence(accepted_entities_text, sentence)]
    #
    # print("#" * 120)
    # print("Selected sentences")
    # for sent in selected_sentences:
    #     print(sent)
    # print("-" * 120)
    # print("Removed sentences")
    # for sent in removed_sentences:
    #     print(sent)

    return selected_sentences
