import requests
import urllib.parse
import json
import time

URL = 'https://meta.wikimedia.org/beacon/event'


def log_api_request(source, target, seed=None, search=None):
    event = dict(timestamp=int(time.time()),
                 sourceLanguage=source,
                 targetLanguage=target)
    if seed:
        event['seed'] = seed
    if search:
        event['searchAlgorithm'] = search

    payload = dict(schema='TranslationRecommendationAPIRequests',
                   revision=15405506,
                   wiki='metawiki',
                   event=event)

    url = URL + '?' + urllib.parse.quote_plus(json.dumps(payload))

    try:
        requests.get(url)
    except requests.exceptions.RequestException:
        pass
