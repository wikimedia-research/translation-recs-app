import requests
import random
from datetime import datetime
from dateutil import relativedelta
from collections import OrderedDict
import json
import time
import multiprocessing as mp

#from google import search

def get_seeded_recommendations(s, t, seed, n):
    """
    Returns n articles in s missing in t based on a search for seed
    """
    #return  [{"pageviews": 233735, "wikidata_id": "", "title": "Lincoln's_Lost_Speech"}, {"pageviews": 120015, "wikidata_id": "", "title": "Tracking_(education)"}]
    titles = wiki_search(s, seed, 3*n)
    if len(titles) ==0:
        print('No Search Results')
        return []

    titles = filter_missing(s, t, titles)[:n]
    if len(titles) == 0:
        print('All articles exist in target')
        return []

    article_pv_dict = get_article_views_parallel(s, titles)
    ret =  [{'title': a, 'pageviews': article_pv_dict[a],'wikidata_id': ''} for a in titles]
    return  [{"pageviews": 233735, "wikidata_id": "", "title": "Lincoln's_Lost_Speech"}, {"pageviews": 120015, "wikidata_id": "", "title": "Tracking_(education)"}]



def get_global_recommendations(s, t, n):
    """
    Returns n most viewd articles yesterday in s missing in t
    """
    article_pv_dict = get_top_article_views(s)
    # dont include top hits and limit the number to filter
    titles = list(article_pv_dict.keys())[3:300] 
    titles = filter_missing(s, t, titles)[:n]
    ret =  [{'title': a, 'pageviews': article_pv_dict[a],'wikidata_id': ''} for a in titles]
    return ret




def get_top_article_views(s):
    """
    Get top viewd articles from pageview api
    """
    dt = (datetime.utcnow() - relativedelta.relativedelta(days=2)).strftime('%Y/%m/%d')
    query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/%s.wikipedia/all-access/%s" % (s, dt)
    response = requests.get(query).json()
    article_pv_dict = OrderedDict()

    try:
        for d in json.loads(response['items'][0]['articles']):
            if 'article' in d and ':' not in d['article'] and not d['article'].startswith('List'):
                article_pv_dict[d['article']] =  d['views']
    except:
        print('PV TOP Article API response malformed')
    return article_pv_dict



def get_article_views_parallel(s, articles):
    """
    Get the number of pageviews in the last 14 days for each article
    """
    p = mp.Pool(len(articles))
    return dict(p.map(get_article_views, [(s, a) for a in articles]))


def get_article_views(arg_tuple):
    """
    Get pv counts for a single article from pv api
    """
    s = arg_tuple[0]
    article = arg_tuple[1]
    start = (datetime.utcnow() - relativedelta.relativedelta(days=1)).strftime('%Y%m%d00')
    stop = (datetime.utcnow() - relativedelta.relativedelta(days=15)).strftime('%Y%m%d00')
    query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/%s.wikipedia/all-access/user/%s/daily/%s/%s"
    query = query % (s, article, stop, start)
    response = requests.get(query).json()
    if 'items' not in response:
        return (article, 0)
    return (article, sum([x['views'] for x in response['items']]))


def filter_missing(s, t, titles):
    """
    Query wikidata to filer out articles in s that exist in t
    """
    query = 'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks/urls&format=json' % (s, '|'.join(titles))
    response = requests.get(query).json()
    missing = []
    swiki = '%swiki' % s
    twiki = '%swiki' % t
    for k, v in response['entities'].items():
        if 'sitelinks' in v:
            if swiki in v['sitelinks'] and twiki not in v['sitelinks']:
                missing.append(v['sitelinks'][swiki]['title'].replace(' ', '_'))
    return [t for t in titles if t in missing]


def wiki_search(s, seed, n):
    """
    Query wiki search for articles related to seed
    """
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
    response = requests.get(mw_api, params=params).json()['query']['search']
    return [r['title'].replace(' ', '_') for r in response]

"""
def google_search(s, article, n = 10):
    q = 'site:%s.wikipedia.org %s' % (s, article)
    results = list(search(q, stop=n))
    main_articles = []
    for r in results:
        if r.startswith('https://en.wikipedia.org/wiki'):
            r = r[30:]
            if ':' not in r and '%3' not in r:
                main_articles.append(r)
    return main_articles
"""