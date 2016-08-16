import json
import requests
import time
from flask import Blueprint, request, Response

from recommendation.api.filters import apply_filters_chunkwise
from recommendation.api.candidate_finders import PageviewCandidateFinder, MorelikeCandidateFinder
from recommendation.api.pageviews import PageviewGetter
from recommendation.utils import event_logger
from recommendation.utils import configuration
import recommendation

api = Blueprint('api', __name__)

language_pairs = None

finder_map = {
    'morelike': MorelikeCandidateFinder(),
    'mostpopular': PageviewCandidateFinder(),
}


def json_response(dat):
    resp = Response(response=json.dumps(dat),
                    status=200,
                    mimetype='application/json')
    return resp


@api.route('/')
def get_recommendations():
    t1 = time.time()
    args = parse_args(request)

    if not is_valid_language_pair(args['s'], args['t']):
        return json_response({'error': 'Invalid or duplicate source and/or target language'})

    recs = recommend(
        args['s'],
        args['t'],
        args['finder'],
        seed=args['article'],
        n_recs=args['n'],
        pageviews=args['pageviews']
    )

    if len(recs) == 0:
        msg = 'Sorry, failed to get recommendations'
        return json_response({'error': msg})

    event_logger.log_api_request(
        source=args['s'],
        target=args['t'],
        seed=args['article'],
        search=args['search']
    )

    t2 = time.time()
    print('Total:', t2 - t1)

    return json_response({'articles': recs})


def is_valid_language_pair(source, target):
    if source == target:
        return False

    global language_pairs
    if language_pairs is None:
        config = configuration.get_configuration(recommendation.config_path, recommendation.__name__,
                                                 recommendation.config_name)
        language_pairs_endpoint = config.get('endpoints', 'language_pairs')
        try:
            result = requests.get(language_pairs_endpoint)
            result.raise_for_status()
            pairs = result.json()
        except requests.exceptions.RequestsException:
            return
        language_pairs = pairs

    if source not in language_pairs['source'] or target not in language_pairs['target']:
        return False
    return True


def parse_args(request):
    """
    Parse api query parameters
    """
    n = request.args.get('n')
    try:
        n = min(int(n), 24)
    except:
        n = 12

    # Get search algorithm
    if not request.args.get('article'):
        search = 'mostpopular'
    else:
        search = request.args.get('search')
        if search not in ('morelike',):
            search = 'morelike'
    finder = finder_map[search]

    # determine if client wants pageviews
    pageviews = request.args.get('pageviews')
    if pageviews == 'false':
        pageviews = False
    else:
        pageviews = True

    args = {
        's': request.args.get('s'),
        't': request.args.get('t'),
        'article': request.args.get('article', ''),
        'n': n,
        'search': search,
        'finder': finder,
        'pageviews': pageviews,
    }

    return args


def recommend(s, t, finder, seed=None, n_recs=10, pageviews=True, max_candidates=500):
    """
    1. Use finder to select a set of candidate articles
    2. Filter out candidates that are not missing, are disambiguation pages, etc
    3. get pageview info for each passing candidate if desired
    """

    recs = []
    for seed in seed.split('|'):
        recs += finder.get_candidates(s, seed, max_candidates)
    recs = sorted(recs, key=lambda x: x.rank)

    recs = apply_filters_chunkwise(s, t, recs, n_recs)

    if pageviews:
        recs = PageviewGetter().get(s, recs)

    recs = sorted(recs, key=lambda x: x.rank)
    return [{'title': r.title, 'pageviews': r.pageviews, 'wikidata_id': r.wikidata_id} for r in recs]


@api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
