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
    t1 = time.time()
    titles = wiki_search(s, seed, 3*n)
    t2 = time.time()
    print('Search:', t2-t1)
    titles = filter_missing(s, t, titles)[:n]
    t3 = time.time()
    print('Filter:', t3-t2)
    article_pv_dict = get_article_views_parallel(s, titles)
    ret =  [{'title': a, 'pageviews': article_pv_dict[a],'wikidata_id': ''} for a in titles]
    t4 = time.time()
    print('Pageviews:', t4-t3)
    return ret

def get_global_recommendations(s, t, n):
    t1 = time.time()
    article_pv_dict = get_top_article_views(s)
    t2 = time.time()
    print('Get Top:', t2-t1)
    titles = list(article_pv_dict.keys())[3:300]
    titles = filter_missing(s, t, titles)[:n]
    t3 = time.time()
    print('Filter:', t3-t2)
    ret =  [{'title': a, 'pageviews': article_pv_dict[a],'wikidata_id': ''} for a in titles]
    return ret




def get_top_article_views(s):
    dt = (datetime.utcnow() - relativedelta.relativedelta(days=2)).strftime('%Y/%m/%d')
    query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/%s.wikipedia/all-access/%s" % (s, dt)
    response = requests.get(query).json()
    article_pv_dict = OrderedDict()
    for d in json.loads(response['items'][0]['articles']):
        if 'article' in d and ':' not in d['article'] and not d['article'].startswith('List'):
            article_pv_dict[d['article']] =  d['views']
    return article_pv_dict



def wiki_search(s, article, n):
    mw_api = 'https://%s.wikipedia.org/w/api.php' % s
    params = {
        'action': 'query',
        'list': 'search',
        'format': 'json',
        'srsearch': article,
        'srnamespace' : 0,
        'srwhat': 'text',
        'srprop': 'wordcount',
        'srlimit': n

    }
    response = requests.get(mw_api, params=params).json()['query']['search']
    return [r['title'].replace(' ', '_') for r in response]

def get_article_views_parallel(s, articles):
    p = mp.Pool(len(articles))
    return dict(p.map(get_article_views, [(s, a) for a in articles]))


def get_article_views(arg_tuple):
        s = arg_tuple[0]
        article = arg_tuple[1]
        start = (datetime.utcnow() - relativedelta.relativedelta(days=1)).strftime('%Y%m%d00')
        stop = (datetime.utcnow() - relativedelta.relativedelta(days=15)).strftime('%Y%m%d00')
        query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/%s.wikipedia/all-access/user/%s/daily/%s/%s"
        query = query % (s, article, stop, start)
        response = requests.get(query).json()
        return (article, sum([x['views'] for x in response['items']]))


def filter_missing(s, t, titles):
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