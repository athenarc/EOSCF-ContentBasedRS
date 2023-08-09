import spacy
import re
import pytextrank
from nltk.stem.porter import PorterStemmer

class TextProcessor:

    def __init__(self, spacy_model_name):
        self.spacy_nlp = spacy.load(spacy_model_name)
        self.stemmer = PorterStemmer()

        self.spacy_nlp.add_pipe("textrank")
        self.spacy_pipeline_adds_on = ["textrank"]

    @staticmethod
    def cleaning(text: str, extra_rules:dict[str, str]=None):
        """
        Args:
            text (str)
            extra_rules (dict[str, str]): The additional replacements that will be applied to clean the text

        """
        text = re.sub('<[^<]+?>', '', text)

        text = text.replace('\n', '.')
        text = text.replace('**', '')

        if extra_rules is not None:
            for old, new in extra_rules.items():
                text = text.replace(old, new)

        return text

    def normalization(self, texts: list[str]):
        normalized_texts = []
        for text in texts:
            # Lowercase
            text = text.lower()

            doc = self.spacy_nlp(text, disable=self.spacy_pipeline_adds_on)

            # Remove stopwords and punctuation
            preprocessed_words = []
            for word in doc:
                # Remove stopwords and punctuation
                if not word.is_stop and not word.is_punct:
                    # Lemmatize
                    preprocessed_words.append(word.lemma_)

            normalized_texts.append(" ".join(preprocessed_words))

        return normalized_texts

    def stemming(self, text):
        return " ".join([self.stemmer.stem(token.text) for token in self.spacy_nlp(text, disable=self.spacy_pipeline_adds_on)])

    def lemmatization(self, text):
        return " ".join([token.lemma_ for token in self.spacy_nlp(text)])

    def textrank(self, text):
        return self.spacy_nlp(text)._.phrases

    def ner(self, text):
        return self.spacy_nlp(text, disable=self.spacy_pipeline_adds_on).ents

    def sentencizer(self, text):
        return self.spacy_nlp(text, disable=self.spacy_pipeline_adds_on).sents

    def remove_stopwords(self, text):
        return " ".join([token.text for token in
                         self.spacy_nlp(text, disable=self.spacy_pipeline_adds_on) if not token.is_stop])
