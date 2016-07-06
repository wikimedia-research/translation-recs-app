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
import random


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

    # shuffle
    top_article_pv_dict = OrderedDict(sorted(top_article_pv_dict.items(), key=lambda x: random.random()))


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


