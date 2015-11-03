import requests
import random
from datetime import datetime
from dateutil import relativedelta
from collections import OrderedDict, defaultdict
import json
import time
import multiprocessing as mp
import concurrent.futures
#from google import search

def get_seeded_recommendations(s, t, seed, n, pageviews=True):
    """
    Returns n articles in s missing in t based on a search for seed
    """
    articles = wiki_search(s, seed, 3*n)
    if len(articles) ==0:
        print('No Search Results')
        return []

    missing_article_id_dict = filter_missing(s, t, articles)
    missing_articles = [a for a in articles if a in missing_article_id_dict][:n] #keep search ranking order

    if len(missing_articles) == 0:
        print('All articles exist in target')
        return []

    missing_article_pv_dict  = defaultdict(int)

    if pageviews:
        missing_article_pv_dict = get_article_views_threaded(s, missing_articles)
        #missing_article_pv_dict = dict(get_article_views((s,t)) for t in missing_article_id_dict.keys())

    ret =  [{'title': a,
             'pageviews': missing_article_pv_dict[a],
             'wikidata_id': missing_article_id_dict[a]} for a in missing_articles]

    return ret


def get_global_recommendations(s, t, n):
    """
    Returns n most viewd articles yesterday in s missing in t
    """
    top_article_pv_dict = get_top_article_views(s)
    # dont include top hits and limit the number to filter
    top_articles = list(top_article_pv_dict.keys())[3:300] 
    top_missing_articles_id_dict = filter_missing(s, t, top_articles)
    top_missing_articles = [a for a in top_articles if a in top_missing_articles_id_dict][:n]

    ret =  [{'title': a, 'pageviews': top_article_pv_dict[a],'wikidata_id': top_missing_articles_id_dict[a]} for a in top_missing_articles]
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
    Get the number of pageviews in the last 14 days for each article.
    Does not play nice with uwsgi
    """
    p_pool = mp.Pool(4)
    return dict(p_pool.map(get_article_views, [(s, a) for a in articles]))


def get_article_views_threaded(s, articles):
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        result = executor.map(get_article_views, [(s, a) for a in articles])
        return dict(result)

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
    Query wikidata to filter out articles in s that exist in t. Returns
    a dict of missing articles and their wikidata ids
    """
    query = 'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks/urls&format=json' % (s, '|'.join(titles))
    response = requests.get(query).json()
    missing_article_id_dict = {}
    swiki = '%swiki' % s
    twiki = '%swiki' % t
    for k, v in response['entities'].items():
        if 'sitelinks' in v:
            if swiki in v['sitelinks'] and twiki not in v['sitelinks']:
                title = v['sitelinks'][swiki]['title'].replace(' ', '_')
                missing_article_id_dict[title] = k
    return missing_article_id_dict


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