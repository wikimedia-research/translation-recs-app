import requests

from recommendation.utils import configuration

_language_pairs = None


def is_valid_language_pair(source, target):
    if source == target:
        return False

    try:
        initialize_language_pairs()
    except ConnectionError:
        # If we can't fetch a list of language pairs and it is the case that they are invalid,
        #  then the api will break downstream. is_valid_language_pair() is meant to short-circuit
        #  that failure, but is not essential
        return True

    if source not in _language_pairs['source'] or target not in _language_pairs['target']:
        return False
    return True


def initialize_language_pairs():
    global _language_pairs
    if _language_pairs is None:
        language_pairs_endpoint = configuration.get_config_value('endpoints', 'language_pairs')
        try:
            result = requests.get(language_pairs_endpoint)
            result.raise_for_status()
            pairs = result.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError('Unable to load data from {}. {}'.format(language_pairs_endpoint, e))
        _language_pairs = pairs


def get_language_pairs():
    initialize_language_pairs()
    return _language_pairs
