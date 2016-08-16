import pytest
import responses
import re
import requests

from recommendation.api import candidate_finders

MATCH_ALL = re.compile(r'.')


@pytest.mark.parametrize('count', [
    0,
    10
])
def test_finder_does_not_return_too_many(finder, count):
    result = finder.get_candidates('en', None, count)
    assert count >= len(result)


def test_inheritance(finder):
    assert isinstance(finder, candidate_finders.CandidateFinder)


def test_invalid_language_returns_empty_list(finder):
    result = finder.get_candidates('qqq', None, 1)
    assert [] == result


@pytest.mark.parametrize('body,status', [
    ('', 404),
    (requests.HTTPError('mocked exception'), 0)
])
@responses.activate
def test_finder_returns_empty_list_when_requests_breaks(finder, body, status):
    responses.add(responses.GET, MATCH_ALL, body=body, status=status, content_type='application/text')
    assert [] == finder.get_candidates('en', None, 10)
