import requests
import random
from datetime import datetime
from dateutil import relativedelta
from collections import OrderedDict, defaultdict
import json
import time
import multiprocessing as mp
import concurrent.futures
import math
import itertools
from pprint import pprint

def search(s, seed, n, search_alg):
    """
    s: source language
    seed: queries/articles seperated by pipe
    n: final number of recommendations requested
    Does a concurrent search for seeds using search_alg
    """
    terms = seed.split('|')
    n_total = 5.0*n # boost to avoid counteract filter
    n_per_term = math.ceil(n_total/ len(terms))

    if search_alg =='wiki':
        search_function = standard_wiki_search
    else:
        search_function = morelike_wiki_search

    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        f = lambda args: search_function(*args)
        results = executor.map(f, [(s, term, n_per_term) for term in terms])
        article_lists = []
        error_messages = set()
        for recs, msg in results:
            if recs:
                article_lists.append(list(recs))
            if msg:
                error_messages.add(msg)

        if len(error_messages) == 0:
            error_message = None
        else:
            error_message = ' '.join(error_messages)

        if len(article_lists) == 0:
            return None, error_message
        else:
            return list(itertools.chain(*zip(*article_lists))), None # if there is something its ok
        




def get_seeded_recommendations(s, t, seed, n, pageviews, search_alg):
    """
    Returns n articles in s missing in t based on a search for seed
    """

    articles, error = search(s, seed, n, search_alg)

    if not articles:
        return None, error

    missing_article_id_dict = find_missing(s, t, articles)
    disambiguation_pages = find_disambiguation(s, missing_article_id_dict.keys())

    missing_articles = [ a for a in articles \
                         if a in missing_article_id_dict \
                         and a not in disambiguation_pages][:n] #keep search ranking order

    if len(missing_articles) == 0:
        return None, 'None of the articles similar to %s in %s that are linked to Wikidata and are missing in %s' % (seed, s, t)

    missing_article_pv_dict  = defaultdict(int)

    if pageviews:
        missing_article_pv_dict = get_article_views_threaded(s, missing_articles)

    recs =  [{'title': a,
             'pageviews': missing_article_pv_dict[a],
             'wikidata_id': missing_article_id_dict[a]} for a in missing_articles]

    return recs, None


def get_global_recommendations(s, t, n):
    """
    Returns n most viewd articles yesterday in s missing in t
    """
    top_article_pv_dict = get_top_article_views(s)

    if len(top_article_pv_dict) == 0:
        return None, "Could not get most popular articles for %s from pageview API. Try using a seed article." % s

    # dont include top hits and limit the number to filter
    top_articles = list(top_article_pv_dict.keys())
    if '-' in top_articles:
        top_articles.remove('-')

    top_missing_articles_id_dict = {}

    step = 50
    indices = list(zip(range(0, len(top_articles) - step, step), range(step, len(top_articles), step)))
    
    # check top articles in chunks of 50 for missing articles
    for start, stop in indices:
        top_missing_articles_id_dict.update(find_missing(s, t, top_articles[start:stop]))
        if len(top_missing_articles_id_dict) >= n:
            break

    # get n missing articles sorted by view counts
    top_missing_articles = [a for a in top_articles if a in top_missing_articles_id_dict][:n]

    if len(top_missing_articles) == 0:
        return None, "None of the most popular articles in %s that linked to Wikidata are missing in %s" % (s, t)

    recs =  [{'title': a, 'pageviews': top_article_pv_dict[a],'wikidata_id': top_missing_articles_id_dict[a]} for a in top_missing_articles]
    return recs, None


def standard_wiki_search(s, seed, n):
    return wiki_search(s, seed, n, False)


def morelike_wiki_search(s, query, n):
    #get an actual article from seed
    seed_list, msg = wiki_search(s, query, 1, False)

    if seed_list: # we have an article seed
        seed = seed_list[0]
        if seed != query:
            print('Query: %s  Article: %s' % (query, seed))
        results, msg = wiki_search(s, seed, n, True)
        if results:
            results.insert(0, seed)
            print('Succesfull Morelike Search')
            return results, None
        else:
            print('Failed Morelike Search. Reverting to standard search')
            return wiki_search(s, query, n, False)
    else:
        return None, msg


def wiki_search(s, seed, n, morelike):
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
        return None, 'Could not search for articles related to seed in %s. Choose another language.' % s

    if 'query' not in response or 'search' not in response['query']:
        return None, 'Could not search for articles related to seed in %s. Choose another language.' % s

    response = response['query']['search']
    results =  [r['title'].replace(' ', '_') for r in response]
    if len(results) == 0:
        return None, 'No articles similar to %s in %s. Try another seed.' % (seed, s)

    return results, None



def find_missing(s, t, titles):
    """
    Query wikidata to find articles in s that exist in t. Returns
    a dict of missing articles and their wikidata ids
    """

    missing_article_id_dict = {}
    swiki = '%swiki' % s
    twiki = '%swiki' % t

    def query_wikidata(titles):
        query_template = 'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks/urls&format=json' 
        query = query_template % (s, '|'.join(titles))
        response = requests.get(query)
        if response:
            return response.json()
        else:
            print('Bad Wikidata API response')
            return {}

    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        chunk_size = 10
        chunks = [titles[i:i+chunk_size] for i in range(0, len(titles), chunk_size)]
        results = executor.map(query_wikidata, chunks)
    

    for result in results:

        if 'entities' not in result:
            print ('None of the titles have a Wikidata Item')
            continue

        for k, v in result['entities'].items():
            if 'sitelinks' in v:
                if swiki in v['sitelinks'] and twiki not in v['sitelinks']:
                    title = v['sitelinks'][swiki]['title'].replace(' ', '_')
                    missing_article_id_dict[title] = k

        if len(missing_article_id_dict) == 0:
            print("None of the source articles missing in the target")

    return missing_article_id_dict



def find_disambiguation(s, titles):
    """
    Returns the subset of titles that are disambiguation pages
    """
    if len(titles) ==0:
        print('No Disambiguation pages: titles list is empty')
        return set()

    query = 'https://%s.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=disambiguation&format=json&titles=%s' % (s, '|'.join(titles))
    response = requests.get(query).json()
    disambiguation = set()

    if 'query' not in response and 'pages' not in response['query']:
        print('Error finding disambiguation pages')
        return set()

    for k,v in response['query']['pages'].items():
        if 'pageprops' in v and 'disambiguation' in v['pageprops']:
            title = v['title'].replace(' ', '_')
            disambiguation.add(title)
    return disambiguation    



def get_top_article_views(s):
    """
    Get top viewd articles from pageview api
    """
    dt = (datetime.utcnow() - relativedelta.relativedelta(days=2)).strftime('%Y/%m/%d')
    query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/%s.wikipedia/all-access/%s" % (s, dt)
    response = requests.get(query).json()
    article_pv_dict = OrderedDict()
    # when T118913 is fixed, parse response with json
    try:
        for d in response['items'][0]['articles']:
            if 'article' in d and ':' not in d['article'] and not d['article'].startswith('List'):
                article_pv_dict[d['article']] =  d['views']
    except:
        print('PV API response malformed')
    return article_pv_dict



def get_article_views_threaded(s, articles):
    """
    Get the number of pageviews in the last 14 days for each article.
    """

    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        f = lambda args: get_article_views(*args)
        result = executor.map(f, [(s, a) for a in articles])
        return dict(result)


def get_article_views(s, article):
    """
    Get pv counts for a single article from pv api
    """
    
    start = (datetime.utcnow() - relativedelta.relativedelta(days=1)).strftime('%Y%m%d00')
    stop = (datetime.utcnow() - relativedelta.relativedelta(days=15)).strftime('%Y%m%d00')
    query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/%s.wikipedia/all-access/user/%s/daily/%s/%s"
    query = query % (s, article, stop, start)
    response = requests.get(query).json()
    if 'items' not in response:
        return (article, 0)
    return (article, sum([x['views'] for x in response['items']]))








