import pytest
import responses
import re

from recommendation.api import filters
from recommendation.utils import configuration

SOURCE = 'xx'


@pytest.fixture(params=[
    filters.MissingFilter,
    filters.DisambiguationFilter
])
def the_filter(request):
    return request.param()


def query(the_filter):
    filter_type = type(the_filter)
    if filter_type is filters.MissingFilter:
        return the_filter.query_wikidata_sitelinks(SOURCE, '')
    if filter_type is filters.DisambiguationFilter:
        return the_filter.query_disambiguation_pages(SOURCE, '')


def get_expected_endpoint(the_filter):
    filter_type = type(the_filter)
    if filter_type is filters.MissingFilter:
        return configuration.get_config_value('endpoints', 'wikidata')
    if filter_type is filters.DisambiguationFilter:
        return configuration.get_config_value('endpoints', 'wikipedia').format(source=SOURCE)


def add_response(body='', json=None, status=200):
    responses.add(responses.GET, re.compile('.'), body=body, json=json, status=status)


def test_queries_correct_endpoint(the_filter):
    add_response()
    query(the_filter)
    assert 1 == len(responses.calls)
    assert get_expected_endpoint(the_filter) in responses.calls[0].request.url


def test_bad_url(the_filter):
    result = query(the_filter)
    assert {} == result


def test_404(the_filter):
    add_response(json={'valid': 'json'}, status=404)
    result = query(the_filter)
    assert {} == result


def test_bad_json(the_filter):
    add_response(body='This is not valid json.')
    result = query(the_filter)
    assert {} == result
