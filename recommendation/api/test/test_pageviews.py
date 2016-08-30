import pytest
import responses
import datetime
import re

from recommendation.api import pageviews
from recommendation.api import utils
from recommendation.utils import configuration

TITLE = 'Sample_Title'
SOURCE = 'xx'
GOOD_RESPONSE = {
    'items': [
        {'project': '{source}.wikipedia'.format(source=SOURCE),
         'article': TITLE,
         'granularity': 'daily',
         'timestamp': '2016010100',
         'access': 'all-access',
         'agent': 'user',
         'views': 1234},
        {'project': '{source}.wikipedia'.format(source=SOURCE),
         'article': TITLE,
         'granularity': 'daily',
         'timestamp': '2016010200',
         'access': 'all-access',
         'agent': 'user',
         'views': 5678}
    ]
}


def add_response(body='', json=None, status=200):
    responses.add(responses.GET, re.compile('.'), body=body, json=json, status=status)


def run_getter():
    getter = pageviews.PageviewGetter()
    article = utils.Article(TITLE)
    result = getter.helper(SOURCE, article)
    assert result is article
    return result


def test_pageviews():
    add_response(json=GOOD_RESPONSE)
    article = run_getter()
    assert sum([item['views'] for item in GOOD_RESPONSE['items']]) == article.pageviews


@pytest.mark.parametrize('add,body,json,status', [
    (False, '', None, 200),
    (True, '', {'valid': 'json'}, 404),
    (True, 'This is not valid json.', None, 200)
])
def test_getter_failures(add, body, json, status):
    if add:
        add_response(body=body, json=json, status=status)
    article = run_getter()
    assert 0 == article.pageviews


def test_getter_queries_correct_url():
    add_response()
    run_getter()
    assert 1 == len(responses.calls)
    assert configuration.get_config_value('endpoints', 'pageviews') in responses.calls[0].request.url
    assert pageviews.get_pageview_query_url(SOURCE, TITLE) == responses.calls[0].request.url


def test_date_range(monkeypatch):
    static_date = datetime.datetime(2010, 1, 20, 0, 0, 0)

    class mockdatetime:
        @classmethod
        def utcnow(cls):
            return static_date
    monkeypatch.setattr(datetime, 'datetime', mockdatetime)
    add_response()
    run_getter()
    assert '2010010500/2010011900' in responses.calls[0].request.url
