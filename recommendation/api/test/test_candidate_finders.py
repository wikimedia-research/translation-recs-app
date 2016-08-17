import pytest
import responses
import requests
import urllib
import json
import re

from recommendation.api import candidate_finders

PAGEVIEW_RESPONSE = {
    'items': [
        {
            'access': 'all-access',
            'month': '08',
            'day': '16',
            'year': '2016',
            'project': 'en.wikipedia',
            'articles': [
                {'article': 'Sample_A', 'rank': 1, 'views': 20},
                {'article': 'Sample_B', 'rank': 2, 'views': 19},
                {'article': 'Sample_C', 'rank': 3, 'views': 18},
                {'article': 'Sample_D', 'rank': 4, 'views': 17},
                {'article': 'Sample_E', 'rank': 5, 'views': 16},
                {'article': 'Sample_F', 'rank': 6, 'views': 15},
                {'article': 'Sample_G', 'rank': 7, 'views': 14},
                {'article': 'Sample_H', 'rank': 8, 'views': 13},
                {'article': 'Sample_I', 'rank': 9, 'views': 12},
                {'article': 'Sample_J', 'rank': 10, 'views': 11},
                {'article': 'Sample_K', 'rank': 11, 'views': 10},
                {'article': 'Sample_L', 'rank': 12, 'views': 9}
            ]
        }
    ]
}

BAD_PAGEVIEW_RESPONSE = {
    'detail': ('The date(s) you used are valid, but we either do not have data for those date(s), or the project you '
               'asked for is not loaded yet.  Please check https://wikimedia.org/api/rest_v1/?doc for more '
               'information.'),
    'uri': '/analytics.wikimedia.org/v1/pageviews/top/qqq.wikipedia/all-access/2016/08/16',
    'type': 'https://restbase.org/errors/not_found',
    'method': 'get',
    'title': 'Not found.'
}

MORELIKE_RESPONSE = {
    'batchcomplete': '',
    'query': {
        'searchinfo': {'totalhits': 100},
        'search': [
            {'ns': 0, 'wordcount': 1001, 'title': 'A'},
            {'ns': 0, 'wordcount': 1002, 'title': 'B'},
            {'ns': 0, 'wordcount': 1003, 'title': 'C'},
            {'ns': 0, 'wordcount': 1004, 'title': 'D'},
            {'ns': 0, 'wordcount': 1005, 'title': 'E'},
            {'ns': 0, 'wordcount': 1006, 'title': 'F'},
            {'ns': 0, 'wordcount': 1007, 'title': 'G'},
            {'ns': 0, 'wordcount': 1008, 'title': 'H'},
            {'ns': 0, 'wordcount': 1009, 'title': 'I'},
            {'ns': 0, 'wordcount': 1010, 'title': 'J'},
            {'ns': 0, 'wordcount': 1011, 'title': 'K'},
            {'ns': 0, 'wordcount': 1012, 'title': 'L'}
        ]
    },
    'continue': {'sroffset': 12, 'continue': '-||'}
}

EMPTY_WIKI_RESPONSE = {
    'batchcomplete': '',
    'query': {
        'searchinfo': {'totalhits': 0},
        'search': []
    }
}


def get_good_response(finder):
    finder_type = type(finder)
    if finder_type is candidate_finders.PageviewCandidateFinder:
        return PAGEVIEW_RESPONSE
    if finder_type is candidate_finders.MorelikeCandidateFinder:
        return MORELIKE_RESPONSE
    return {}


def get_bad_response(finder):
    finder_type = type(finder)
    if finder_type is candidate_finders.PageviewCandidateFinder:
        return BAD_PAGEVIEW_RESPONSE
    return {}


def add_response(body, status):
    responses.add(responses.GET, re.compile(r'http://localhost.'), body=body, status=status,
                  content_type='application/json')


@pytest.fixture(params=[
    candidate_finders.PageviewCandidateFinder,
    candidate_finders.MorelikeCandidateFinder
])
def finder(request):
    return request.param()


@pytest.mark.parametrize('count', [
    0,
    10
])
def test_finder_returns_correct_amount(finder, count):
    add_response(json.dumps(get_good_response(finder)), 200)
    result = finder.get_candidates('en', None, count)
    assert count == len(result)


def test_inheritance(finder):
    assert isinstance(finder, candidate_finders.CandidateFinder)


def test_invalid_language_returns_empty_list(finder):
    add_response(body=json.dumps(get_bad_response(finder)), status=404)
    result = finder.get_candidates('qqq', None, 1)
    assert [] == result


@pytest.mark.parametrize('body,status', [
    ('', 404),
    ('bad json', 200),
    (requests.HTTPError('mocked exception'), 0)
])
def test_finder_returns_empty_list_when_requests_breaks(finder, body, status):
    add_response(body=body, status=status)
    assert [] == finder.get_candidates('en', None, 10)


def test_finder_calls_go_through_responses(finder):
    if type(finder) is candidate_finders.MorelikeCandidateFinder:
        # the number of calls is determined by other factors
        # that are tested more thoroughly elsewhere
        return
    add_response(body=json.dumps(get_good_response(finder)), status=200)
    finder.get_candidates('en', None, 10)
    assert 1 == len(responses.calls)
    url = responses.calls[0].request.url
    assert 'http://localhost' == url[:16]


@pytest.mark.parametrize('seed,query,expected_calls,seed_response,morelike_response', [
    ('A', 'A', 2, MORELIKE_RESPONSE, MORELIKE_RESPONSE),
    ('B', 'A', 2, MORELIKE_RESPONSE, MORELIKE_RESPONSE),
    ('A', 'A', 1, EMPTY_WIKI_RESPONSE, MORELIKE_RESPONSE),
    ('Z', 'A', 3, MORELIKE_RESPONSE, EMPTY_WIKI_RESPONSE)
])
def test_wiki_search_paths(seed, query, expected_calls, seed_response, morelike_response):
    """
    This function is a mess, but it tries to build and execute the various paths through
     the morelike candidate finder

    :param seed: the user-supplied seed when performing a search
    :param query: after performing the first wiki_search, the top result is used for the subsequent searches
                  this param is used to mock that value when building the url
    :param expected_calls: how many calls are expected to go through `responses`
    :param seed_response: the response to the initial seed_list query
    :param morelike_response: the response to the morelike query
    """
    finder = candidate_finders.MorelikeCandidateFinder()
    search_pattern = dict(
        seed=(seed, 1, False, seed_response),
        morelike=(query, 10, True, morelike_response),
        fallback=(query, 10, False, MORELIKE_RESPONSE)
    )
    for query, count, morelike, response in search_pattern.values():
        url, params = candidate_finders.build_wiki_search('en', query, count, morelike)
        url += '?' + urllib.parse.urlencode(params)
        responses.add(responses.GET, url, json=response, status=200, match_querystring=True)
    finder.get_candidates('en', seed, 10)
    assert expected_calls == len(responses.calls)
