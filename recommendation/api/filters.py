import itertools
import logging
import requests

from recommendation.api.utils import thread_function, chunk_list
from recommendation.utils import configuration

log = logging.getLogger(__name__)


class Filter:
    """
    Filter interface
    """

    def filter_subset(self, s, t, articles):
        return []

    def filter(self, s, t, articles):
        """
        Wrapper to do filtering on chunks of
        articles concurrently
        """
        chunks = chunk_list(articles, 10)
        args_list = [(s, t, chunk) for chunk in chunks]
        results = thread_function(self.filter_subset, args_list)
        return list(itertools.chain.from_iterable(results))


class MissingFilter(Filter):
    """
    Class for filtering out which articles from
    source language s already exist in target language t
    using Wikidata sitelinks
    """

    def query_wikidata_sitelinks(self, s, titles):
        """
        Query Wikidata API for the sitelinks for each
        article in titles.
        """

        api = configuration.get_config_value('endpoints', 'wikidata')
        params = configuration.get_config_dict('wikidata_params')
        params['sites'] = params['sites'].format(source=s)
        params['titles'] = '|'.join(titles)

        try:
            response = requests.get(api, params=params)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            log.info('Bad Wikidata API response')
            return {}

    def parse_wikidata_sitelinks_data(self, s, t, data):
        """
        Given sitelinks data, return a dict mapping from
        article titles to Wikidata ids for the articles in s
        missing in t
        """

        title_id_dict = {}
        swiki = '%swiki' % s
        twiki = '%swiki' % t

        if 'entities' not in data:
            log.info('None of the titles have a Wikidata Item')
            return title_id_dict

        for k, v in data['entities'].items():
            if 'sitelinks' in v:
                if swiki in v['sitelinks'] and twiki not in v['sitelinks']:
                    title = v['sitelinks'][swiki]['title'].replace(' ', '_')
                    title_id_dict[title] = k

        if len(title_id_dict) == 0:
            log.info('None of the source articles missing in the target')

        return title_id_dict

    def filter_subset(self, s, t, articles):
        """
        Remove articles in s that already exist in t
        using Wikidata sitelinks from the Wikidata API
        """

        d = {a.title: a for a in articles}
        titles = [a.title for a in articles]

        data = self.query_wikidata_sitelinks(s, titles)
        title_id_dict = self.parse_wikidata_sitelinks_data(s, t, data)

        filtered_articles = []

        for title, wikidata_id in title_id_dict.items():
            article = d[title]
            article.wikidata_id = wikidata_id
            filtered_articles.append(article)

        return filtered_articles


class DisambiguationFilter(Filter):
    """
    Utility class for filtering out disambiguation
    pages using the Mediawiki API
    """

    def query_disambiguation_pages(self, s, titles):
        api = configuration.get_config_value('endpoints', 'wikipedia').format(source=s)
        params = configuration.get_config_dict('disambiguation_params')
        params['titles'] = '|'.join(titles)

        try:
            response = requests.get(api, params=params)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            log.info('Bad Disambiguation API response')
            return {}

    def parse_disambiguation_page_data(self, data):
        disambiguation_pages = set()

        if 'query' not in data or 'pages' not in data['query']:
            log.info('Error finding disambiguation pages')
            return set()

        for k, v in data['query']['pages'].items():
            if 'pageprops' in v and 'disambiguation' in v['pageprops']:
                title = v['title'].replace(' ', '_')
                disambiguation_pages.add(title)

        return disambiguation_pages

    def filter_subset(self, s, t, articles):
        titles = [a.title for a in articles]
        data = self.query_disambiguation_pages(s, titles)
        disambiguation_pages = self.parse_disambiguation_page_data(data)
        return [a for a in articles if a.title not in disambiguation_pages]


class TitleFilter(Filter):
    """
    Utility class for filtering out
    articles based on properties of the title alone
    """

    def title_passes(self, title):

        if ':' in title:
            return False
        if title.startswith('List'):
            return False
        return True

    def filter(self, s, t, articles):
        """
        No need to thread this one
        """
        return [a for a in articles if self.title_passes(a.title)]


def apply_filters_chunkwise(s, t, candidates, n_recs, step=100):
    """
    Since filtering is expensive, we want to filter a large list
    of candidates in chunks until we get the desired number of
    passing articles
    """
    filtered_candidates = []
    m = len(candidates)

    indices = [(i, i + step) for i in range(0, m, step)]

    # filter candidates in chunks, stop once we reach n_recs
    for start, stop in indices:
        log.info('Filtering Next Chunk')
        subset = candidates[start:stop]
        subset = MissingFilter().filter(s, t, subset)
        subset = DisambiguationFilter().filter(s, t, subset)
        subset = TitleFilter().filter(s, t, subset)
        filtered_candidates += subset
        if len(filtered_candidates) >= n_recs:
            break

    return filtered_candidates
