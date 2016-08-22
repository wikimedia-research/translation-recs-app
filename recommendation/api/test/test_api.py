import flask
import pytest
import json

from recommendation.api import api

GOOD_RESPONSE = {'articles': [
    {'title': 'A', 'pageviews': 10, 'wikidata_id': 123},
    {'title': 'B', 'pageviews': 11, 'wikidata_id': 122},
    {'title': 'C', 'pageviews': 12, 'wikidata_id': 121},
    {'title': 'D', 'pageviews': 13, 'wikidata_id': 120},
    {'title': 'E', 'pageviews': 14, 'wikidata_id': 119},
    {'title': 'F', 'pageviews': 15, 'wikidata_id': 118},
    {'title': 'G', 'pageviews': 16, 'wikidata_id': 117},
    {'title': 'H', 'pageviews': 17, 'wikidata_id': 116},
]}


@pytest.fixture
def recommend_response(monkeypatch):
    monkeypatch.setattr(api, 'recommend', lambda *args, **kwargs: GOOD_RESPONSE['articles'])


@pytest.fixture
def client():
    app_instance = flask.Flask(__name__)
    app_instance.register_blueprint(api.api)
    return app_instance.test_client()


@pytest.mark.parametrize('target,name,value,expected_status,expected_data', [
    (api, 'is_valid_language_pair', False, 200, {'error': 'Invalid or duplicate source and/or target language'}),
    (api, 'is_valid_language_pair', True, 200, GOOD_RESPONSE)
])
@pytest.mark.usefixtures('recommend_response')
def test_api(client, target, name, value, expected_status, expected_data, monkeypatch):
    monkeypatch.setattr(target, name, lambda *args, **kwargs: value)
    result = client.get('/?s=en&t=de')
    assert expected_status == result.status_code
    assert expected_data == json.loads(result.data.decode('utf-8'))
