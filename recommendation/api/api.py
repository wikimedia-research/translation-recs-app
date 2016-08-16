import json
import requests
import time
from flask import Blueprint, request, Response

from recommendation.api.filters import apply_filters_chunkwise
from recommendation.api.candidate_finders import PageviewCandidateFinder, MorelikeCandidateFinder
from recommendation.api.pageviews import PageviewGetter
from recommendation.utils import event_logger

api = Blueprint('api', __name__)

language_pairs = requests.get('https://cxserver.wikimedia.org/v1/languagepairs').json()

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

    language_error = validate_language_pairs(args)
    if language_error:
        return json_response({'error': language_error})

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


def validate_language_pairs(args):
    """
    Make sure s=!t and that both s and t
    are valid language codes
    """
    s = args['s']
    t = args['t']

    # make sure language codes are valid
    if s not in language_pairs['source'] or t not in language_pairs['target']:
        return 'Invalid source or target language'
    if s == t:
        return 'Source is equal to target language'


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
