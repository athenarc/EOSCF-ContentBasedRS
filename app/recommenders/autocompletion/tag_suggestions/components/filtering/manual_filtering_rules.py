import re
from geotext import GeoText
from wordfreq import word_frequency


def in_filter_out_rules(text: str):
    """
    Returns (boolean): True if any of the manually defined rules can apply to the given text, False otherwise
    """

    # Detect geonames (countries, cities)
    proc_text = GeoText(text)
    if len(proc_text.cities) or len(proc_text.country_mentions):
        return True

    # Detect links
    if re.search(r'(http[s]?://[www.]?)|(www.)', text) is not None:
        return True

    # Detect emails
    if re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text) is not None:
        return True

    # Detect paper references
    if re.search(r'et al.', text) is not None:
        return True

    # Detect common words-phrases
    frequency_threshold = 0.0001
    if word_frequency(text, 'en', wordlist='small') > frequency_threshold:
        return True

    return False
