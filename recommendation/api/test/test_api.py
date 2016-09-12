import flask
import pytest
import json
import urllib.parse

from recommendation.api import api
from recommendation.api import utils
from recommendation.api import filters

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


def get_query_string(input_dict):
    return '/?' + urllib.parse.urlencode(input_dict)


@pytest.fixture
def recommend_response(monkeypatch):
    monkeypatch.setattr(api, 'recommend', lambda *args, **kwargs: GOOD_RESPONSE['articles'])


@pytest.fixture
def client():
    app_instance = flask.Flask(__name__)
    app_instance.register_blueprint(api.api)
    return app_instance.test_client()


@pytest.mark.parametrize('url', [
    get_query_string(dict(s='xx', t='yy')),
    get_query_string(dict(s='xx', t='yy', n=13)),
    get_query_string(dict(s='xx', t='yy', article='separated|list|of|titles')),
    get_query_string(dict(s='xx', t='yy', pageviews='false')),
    get_query_string(dict(s='xx', t='yy', search='morelike')),
])
@pytest.mark.usefixtures('recommend_response')
def test_good_arg_parsing(client, url):
    result = client.get(url)
    assert 200 == result.status_code
    assert GOOD_RESPONSE == json.loads(result.data.decode('utf-8'))


@pytest.mark.parametrize('url', [
    get_query_string(dict(s='xx')),
    get_query_string(dict(t='xx')),
    '/',
    get_query_string(dict(s='xx', t='xx')),
    get_query_string(dict(s='xx', t='yy', n=-1)),
    get_query_string(dict(s='xx', t='yy', n=25)),
    get_query_string(dict(s='xx', t='yy', n='not a number')),
    get_query_string(dict(s='xx', t='yy', article='||||||||||||')),
    get_query_string(dict(s='xx', t='yy', pageviews='not a boolean')),
    get_query_string(dict(s='xx', t='yy', search='not a valid search')),
])
@pytest.mark.usefixtures('recommend_response')
def test_bad_args(client, url):
    result = client.get(url)
    assert 'error' in json.loads(result.data.decode('utf-8'))


@pytest.mark.parametrize('params', [
    dict(s='xx', t='yy'),
])
def test_default_params(params):
    args = api.parse_and_validate_args(params)
    assert 12 == args['count']
    assert '' is args['seed']
    assert True is args['include_pageviews']
    assert 'morelike' == args['search']


def test_recommend(monkeypatch):
    class MockFinder:
        @classmethod
        def get_candidates(cls, s, seed, n):
            return []

    monkeypatch.setattr(api, 'finder_map', {'customsearch': MockFinder})
    args = api.parse_and_validate_args(dict(s='xx', t='yy'))
    args['search'] = 'customsearch'
    result = api.recommend(**args)
    assert [] == result


def test_generated_recommend_response_is_marshalled(client, monkeypatch):
    class MockFinder:
        @classmethod
        def get_candidates(cls, s, seed, n):
            articles = []
            for item in GOOD_RESPONSE['articles']:
                article = utils.Article(item['title'])
                article.pageviews = item['pageviews']
                article.wikidata_id = item['wikidata_id']
                article.rank = article.pageviews
                articles.append(article)
            return articles
    monkeypatch.setattr(api, 'finder_map', {'morelike': MockFinder})
    monkeypatch.setattr(filters, 'apply_filters_chunkwise', lambda source, target, recs, count: recs)
    result = client.get(get_query_string(dict(s='xx', t='yy', pageviews=False)))
    assert GOOD_RESPONSE == json.loads(result.data.decode('utf-8'))
