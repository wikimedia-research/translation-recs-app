import requests
import urllib.parse
import json
import time

URL = 'https://meta.wikimedia.org/beacon/event?'


def log_api_request(source, target, seed=None, search=None):
    event = dict(timestamp=int(time.time()),
                 sourceLanguage=source,
                 targetLanguage=target)
    if seed:
        event['seed'] = seed
    if search:
        event['searchAlgorithm'] = search

    payload = dict(schema='TranslationRecommendationAPIRequests',
                   revision=15395417,
                   wiki='metawiki',
                   event=event)

    url = URL + urllib.parse.quote_plus(json.dumps(payload))

    # print(json.dumps(payload, indent=2))

    r = requests.get(url)

    # print(r.status_code)
    # print(json.dumps(dict(r.headers), indent=2))
