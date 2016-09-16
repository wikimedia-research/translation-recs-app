import requests
import logging
import datetime

from recommendation.utils import configuration

log = logging.getLogger(__name__)


def get(url, params=None):
    log.debug('Get: %s', url)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        log.info('Request failed: {"url": "%s", "error": "%s"}', url, e)
        raise ValueError(e)


def post(url, data=None):
    log.debug('Post: %s', url)
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        log.info('Request failed: {"url": "%s", "error": "%s"}', url, e)
        raise ValueError(e)


def get_disambiguation_pages(source, titles):
    """
    Returns the subset of titles that are disambiguation pages
    """
    endpoint = configuration.get_config_value('endpoints', 'wikipedia').format(source=source)
    params = configuration.get_config_dict('disambiguation_params')
    params['titles'] = '|'.join(titles)

    try:
        data = post(endpoint, data=params)
    except ValueError:
        log.info('Bad Disambiguation API response')
        return []

    pages = data.get('query', {}).get('pages', {}).values()
    return list(set(page['title'].replace(' ', '_') for page in pages if 'disambiguation' in page.get('pageprops', {})))


def get_wikidata_sitelinks(source, target, titles):
    """
    Returns a dictionary mapping from titles to wikidata ids
    for the articles in source missing in target
    """
    endpoint = configuration.get_config_value('endpoints', 'wikidata')
    params = configuration.get_config_dict('wikidata_params')
    params['sites'] = params['sites'].format(source=source)
    params['titles'] = '|'.join(titles)

    title_id_dict = {}
    try:
        data = post(endpoint, data=params)
    except ValueError:
        log.info('Bad Wikidata API response')
        return title_id_dict

    source_wiki = '{}wiki'.format(source)
    target_wiki = '{}wiki'.format(target)

    if 'entities' not in data:
        log.info('None of the titles have a Wikidata Item')
        return title_id_dict

    for wikidata_id, v in data['entities'].items():
        sitelinks = v.get('sitelinks', None)
        if sitelinks:
            if source_wiki in sitelinks and target_wiki not in sitelinks:
                title = sitelinks[source_wiki]['title'].replace(' ', '_')
                title_id_dict[title] = wikidata_id

    if len(title_id_dict) == 0:
        log.info('None of the source articles missing in the target')

    return title_id_dict


def get_pageviews(source, title):
    """
    Get pageview counts for a single article from pageview api
    """
    query = get_pageview_query_url(source, title)

    try:
        response = get(query)
    except ValueError:
        response = {}

    return sum(item['views'] for item in response.get('items', {}))


def get_pageview_query_url(source, title):
    start_days = configuration.get_config_int('single_article_pageviews', 'start_days')
    end_days = configuration.get_config_int('single_article_pageviews', 'end_days')
    query = configuration.get_config_value('single_article_pageviews', 'query')
    start = get_relative_timestamp(start_days)
    end = get_relative_timestamp(end_days)
    query = query.format(source=source, title=title, start=start, end=end)
    return query


def get_relative_timestamp(relative_days):
    date_format = configuration.get_config_value('single_article_pageviews', 'date_format')
    return (datetime.datetime.utcnow() + datetime.timedelta(days=relative_days)).strftime(date_format)
