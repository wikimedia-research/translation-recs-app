import pytest
import responses
import re

from recommendation.api import filters
from recommendation.utils import configuration
from recommendation.api import utils

SOURCE = 'xx'


@pytest.fixture(params=[
    filters.filter_by_missing,
    filters.filter_by_disambiguation
])
def the_filter(request):
    return request.param


def query(the_filter):
    if the_filter is filters.filter_by_missing:
        return the_filter(SOURCE, SOURCE, '')
    if the_filter is filters.filter_by_disambiguation:
        return the_filter(SOURCE, '')


def get_expected_endpoint(the_filter):
    if the_filter is filters.filter_by_missing:
        return configuration.get_config_value('endpoints', 'wikidata')
    if the_filter is filters.filter_by_disambiguation:
        return configuration.get_config_value('endpoints', 'wikipedia').format(source=SOURCE)


def add_response(body='', json=None, status=200):
    responses.add(responses.POST, re.compile('.'), body=body, json=json, status=status)


def test_queries_correct_endpoint(the_filter):
    add_response()
    query(the_filter)
    assert 1 == len(responses.calls)
    assert get_expected_endpoint(the_filter) in responses.calls[0].request.url


def test_bad_url(the_filter):
    result = query(the_filter)
    assert [] == result


def test_404(the_filter):
    add_response(json={'valid': 'json'}, status=404)
    result = query(the_filter)
    assert [] == result


def test_bad_json(the_filter):
    add_response(body='This is not valid json.')
    result = query(the_filter)
    assert [] == result


@pytest.mark.parametrize('title', [
    'Single',
    'Double Word'
])
def test_filter_by_good_title(title):
    candidates = [utils.Article(title)]
    result = filters.filter_by_title(candidates)
    assert candidates == result


@pytest.mark.parametrize('title', [
    'List something blah',
    ': is bad',
    'and cannot appear : anywhere'
])
def test_filter_by_bad_title(title):
    candidates = [utils.Article(title)]
    result = filters.filter_by_title(candidates)
    assert [] == result
