import requests
import urllib.parse
import logging
import json
import time

from recommendation.utils import configuration

log = logging.getLogger(__name__)


def log_api_request(source, target, seed=None, search=None, **kwargs):
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

    url = configuration.get_config_value('endpoints', 'event_logger')
    url += '?' + urllib.parse.quote_plus(json.dumps(payload))

    log.info('Logging event: %s', json.dumps(payload))

    try:
        requests.get(url)
    except requests.exceptions.RequestException:
        pass
