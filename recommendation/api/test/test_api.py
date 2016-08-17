import pytest
import responses
import json

from recommendation.api import api

LANGUAGE_PAIRS = {
    'source': ['aa', 'bb'],
    'target': ['cc', 'dd']
}


def setup_function(function):
    api.language_pairs = None
    responses.add(responses.GET, 'http://localhost', body=json.dumps(LANGUAGE_PAIRS), status=200,
                  content_type='application/json')


@pytest.mark.parametrize('source', LANGUAGE_PAIRS['source'])
@pytest.mark.parametrize('target', LANGUAGE_PAIRS['target'])
def test_language_pairs_valid(source, target):
    assert True is api.is_valid_language_pair(source, target)


@pytest.mark.parametrize('source,target', [
    ('xx', LANGUAGE_PAIRS['target'][0]),
    (LANGUAGE_PAIRS['source'][0], 'xx'),
    ('xx', 'xx')
])
def test_language_pairs_invalid(source, target):
    assert False is api.is_valid_language_pair(source, target)


def test_language_pairs_valid_only_fetches_once():
    assert 0 == len(responses.calls)
    assert True is api.is_valid_language_pair(LANGUAGE_PAIRS['source'][0], LANGUAGE_PAIRS['target'][0])
    assert 1 == len(responses.calls)
    assert True is api.is_valid_language_pair(LANGUAGE_PAIRS['source'][0], LANGUAGE_PAIRS['target'][0])
    assert 1 == len(responses.calls)
