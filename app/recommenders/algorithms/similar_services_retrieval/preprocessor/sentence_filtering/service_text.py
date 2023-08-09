import logging
import re

from app.recommenders.algorithms.similar_services_retrieval.preprocessor.sentence_filtering.entity_base_filtering import \
    sentence_filtering_from_entities
from app.recommenders.algorithms.similar_services_retrieval.preprocessor.sentence_filtering.keyword_based_filtering import \
    sentence_filtering_from_keywords
from app.settings import APP_SETTINGS

logger = logging.getLogger(__name__)


class ServiceText:
    def __init__(self, service_texts):
        self.sentences = self._get_sentences(service_texts)

    @staticmethod
    def sentence_filtering_selector():
        if APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SENTENCE_FILTERING_METHOD"] == "NONE":
            return lambda x: x  # No filtering is applied
        elif APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SENTENCE_FILTERING_METHOD"] == "KEYWORD":
            return sentence_filtering_from_keywords
        elif APP_SETTINGS["BACKEND"]["SIMILAR_SERVICES"]["SENTENCE_FILTERING_METHOD"] == "NER":
            return sentence_filtering_from_entities

    @staticmethod
    def clean_text(text):
        text = text.replace('\n', '.')
        text = text.replace('..', '.')
        text = text.replace('**', '')
        text = text.replace('-', ' ')

        # clean html
        text = re.sub('<[^<]+?>', '', text)

        return text

    def _get_sentences(self, service_text_attributes):
        text_processor = APP_SETTINGS["BACKEND"]["TEXT_PROCESSOR"]
        combined_sentences = []

        for attr, text in service_text_attributes.items():
            sentences = [str(sent) for sent in text_processor.sentencizer(
                text_processor.cleaning(text, extra_rules={'..': '.', '-': ' '}))]
            if attr == 'description':
                # Apply sentence filtering only on description
                filtered_sentences = self.sentence_filtering_selector()(sentences)
                sentences = filtered_sentences if len(filtered_sentences) > 0 else sentences

            combined_sentences.extend(sentences)

        return combined_sentences

    def __str__(self):
        ret = ""
        for ind, sent in enumerate(self.sentences):
            ret += f"{ind}. {sent}\n"
        return ret
