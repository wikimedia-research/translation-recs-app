import requests
import random
from datetime import datetime
from dateutil import relativedelta

class Article:
    """
    Struct containing meta data for an article
    """
    def __init__(self, title):
        self.title = title
        self.wikidata_id = None
        self.rank = None
        self.pageviews = None


class PageviewCandidateFinder():
    """
    Utility Class for getting the most popular articles in a Wikipedia
    """
    
    def query_pageviews(self, s):
        """
        Query pageview API for the most popular articles and parse results
        """
        dt = (datetime.utcnow() - relativedelta.relativedelta(days=2)).strftime('%Y/%m/%d')
        query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/%s.wikipedia/all-access/%s" % (s, dt)
        data =  requests.get(query).json()
        article_pv_tuples = []

        try:
            for d in data['items'][0]['articles']:
                if 'article' in d and ':' not in d['article'] and not d['article'].startswith('List'):
                    article_pv_tuples.append((d['article'], d['views']))
        except:
            print("Could not get most popular articles for %s from pageview API. Try using a seed article." % s)

        return article_pv_tuples


    def get_candidates(self, s, seed, n):
        """
        Return the n most viewed articles
        """

        articles = []
        article_pv_tuples = sorted(self.query_pageviews(s), key=lambda x: random.random())

        for i, t in enumerate(article_pv_tuples):
            a = Article(t[0])
            a.rank = i
            articles.append(a)

        return articles[:n]


class MorelikeCandidateFinder():

    def get_morelike_candidates(self, s, query, n):
        #get an actual article from seed
        seed_list = wiki_search(s, query, 1)

        if seed_list: # we have an article seed
            seed = seed_list[0]
            if seed != query:
                print('Query: %s  Article: %s' % (query, seed))
            results = wiki_search(s, seed, n, morelike=True)
            if results:
                results.insert(0, seed)
                print('Succesfull Morelike Search')
                return results, None
            else:
                print('Failed Morelike Search. Reverting to standard search')
                return wiki_search(s, query, n)
        else:
            return []


    def get_candidates(self, s, seed, n):

        results = self.get_morelike_candidates(s, seed, n)

        articles = []

        for i, title in enumerate(results):
            a = Article(title)
            a.rank = i
            articles.append(a)

        return articles


def wiki_search(s, seed, n, morelike=False):
    """
    Query wiki search for articles related to seed
    """
    if morelike:
        seed = 'morelike:' + seed
    mw_api = 'https://%s.wikipedia.org/w/api.php' % s
    params = {
        'action': 'query',
        'list': 'search',
        'format': 'json',
        'srsearch': seed,
        'srnamespace' : 0,
        'srwhat': 'text',
        'srprop': 'wordcount',
        'srlimit': n
    }
    try:
        response = requests.get(mw_api, params=params).json()
    except:
        print('Could not search for articles related to seed in %s. Choose another language.' % s)
        return [] 

    if 'query' not in response or 'search' not in response['query']:
        print('Could not search for articles related to seed in %s. Choose another language.' % s)
        return []

    response = response['query']['search']
    results =  [r['title'].replace(' ', '_') for r in response]
    if len(results) == 0:
        print('No articles similar to %s in %s. Try another seed.' % (seed, s))
        return []

    return results