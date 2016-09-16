import logging
import time
from flask import Blueprint, request, jsonify

from recommendation.api import filters
from recommendation.api import candidate_finders
from recommendation.api import pageviews
from recommendation.api import specification
from recommendation.utils import event_logger
from recommendation.utils import language_pairs

api = Blueprint('api', __name__)
log = logging.getLogger(__name__)


@api.route('/')
def get_recommendations():
    t1 = time.time()
    try:
        args = parse_and_validate_args(request.args)
    except ValueError as e:
        return jsonify(error=str(e))

    event_logger.log_api_request(**args)
    recs = recommend(**args)

    if len(recs) == 0:
        return jsonify(error='Sorry, failed to get recommendations')

    t2 = time.time()
    log.info('Request processed in %f seconds', t2 - t1)

    return jsonify(specification.marshal_response(recs))


def parse_and_validate_args(args):
    clean_args = specification.parse_and_validate_parameters(args)

    if not language_pairs.is_valid_language_pair(clean_args['source'], clean_args['target']):
        raise ValueError('Invalid or duplicate source and/or target language')

    return clean_args


@api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


finder_map = {
    'morelike': candidate_finders.MorelikeCandidateFinder(),
    'mostpopular': candidate_finders.PageviewCandidateFinder(),
}


def recommend(source, target, search, seed, count, include_pageviews, max_candidates=500):
    """
    1. Use finder to select a set of candidate articles
    2. Filter out candidates that are not missing, are disambiguation pages, etc
    3. get pageview info for each passing candidate if desired
    """

    recs = []

    if seed:
        finder = finder_map[search]
        for seed in seed.split('|'):
            recs.extend(finder.get_candidates(source, seed, max_candidates))
    else:
        recs.extend(finder_map['mostpopular'].get_candidates(source, seed, max_candidates))

    recs = sorted(recs, key=lambda x: x.rank)

    recs = filters.apply_filters(source, target, recs, count)

    if recs and include_pageviews:
        recs = pageviews.set_pageview_data(source, recs)

    recs = sorted(recs, key=lambda x: x.rank)
    return [{'title': r.title, 'pageviews': r.pageviews, 'wikidata_id': r.wikidata_id} for r in recs]
