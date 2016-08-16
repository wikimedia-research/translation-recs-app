import re
import pytest
import responses
import json

from recommendation.api import api

MATCH_ALL = re.compile(r'.')
LANGUAGE_PAIRS = {
    'source': ['aa', 'bb'],
    'target': ['cc', 'dd']
}


@pytest.mark.parametrize('source', LANGUAGE_PAIRS['source'])
@pytest.mark.parametrize('target', LANGUAGE_PAIRS['target'])
@responses.activate
def test_language_pairs_valid(source, target):
    responses.add(responses.GET, MATCH_ALL, body=json.dumps(LANGUAGE_PAIRS), status=200,
                  content_type='application/json')
    assert True is api.is_valid_language_pair(source, target)


@pytest.mark.parametrize('source,target', [
    ('xx', LANGUAGE_PAIRS['target'][0]),
    (LANGUAGE_PAIRS['source'][0], 'xx'),
    ('xx', 'xx')
])
@responses.activate
def test_language_pairs_invalid(source, target):
    responses.add(responses.GET, MATCH_ALL, body=json.dumps(LANGUAGE_PAIRS), status=200,
                  content_type='application/json')
    assert False is api.is_valid_language_pair(source, target)
