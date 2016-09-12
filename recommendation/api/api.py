import logging
import time

from flask import Blueprint, request, jsonify
from pkg_resources import resource_filename
import yaml
from bravado_core import spec
from bravado_core import validate
from bravado_core import marshal
from bravado_core import param

import recommendation.api
from recommendation.api import filters
from recommendation.api import candidate_finders
from recommendation.api import pageviews
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
    log.info('Total: %d', t2 - t1)

    return jsonify(articles=recs)


def parse_and_validate_args(args):
    spec_dict = yaml.load(open(resource_filename(recommendation.api.__name__, 'swagger.yml')).read())
    parsed_spec = spec.Spec.from_dict(spec_dict)

    clean_args = {}
    for parameter in spec_dict['parameters']:
        parameter_spec = spec_dict['parameters'][parameter]
        parameter_type = parameter_spec['type']
        parameter_name = parameter_spec['name']
        try:
            value = param.cast_request_param(parameter_type, parameter, args.get(parameter_name))
            validate.validate_schema_object(parsed_spec, parameter_spec, value)
            clean_args[parameter] = marshal.marshal_schema_object(parsed_spec, parameter_spec, value)
        except Exception as e:
            raise ValueError(e)

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

    finder = finder_map[search]

    recs = []
    for seed in seed.split('|'):
        recs += finder.get_candidates(source, seed, max_candidates)
    recs = sorted(recs, key=lambda x: x.rank)

    recs = filters.apply_filters_chunkwise(source, target, recs, count)

    if include_pageviews:
        recs = pageviews.PageviewGetter().get(source, recs)

    recs = sorted(recs, key=lambda x: x.rank)
    return [{'title': r.title, 'pageviews': r.pageviews, 'wikidata_id': r.wikidata_id} for r in recs]
