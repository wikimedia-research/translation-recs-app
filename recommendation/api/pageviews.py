import requests
import datetime
from dateutil import relativedelta

from recommendation.api.utils import thread_function
from recommendation.utils import configuration


def get_pageview_query_url(source, title):
    start_days = configuration.get_config_int('single_article_pageviews', 'start_days')
    end_days = configuration.get_config_int('single_article_pageviews', 'end_days')
    query = configuration.get_config_value('single_article_pageviews', 'query')
    start = get_relative_timestamp(start_days)
    end = get_relative_timestamp(end_days)
    query = query.format(source=source, title=title, start=start, end=end)
    return query


def get_relative_timestamp(relative_days):
    date_format = configuration.get_config_value('single_article_pageviews', 'date_format')
    return (datetime.datetime.utcnow() + relativedelta.relativedelta(days=relative_days)).strftime(date_format)


class PageviewGetter:
    """
    Utility Class for getting article pageview counts
    via the pageview API
    """

    def helper(self, s, article):
        """
        Get pageview counts for a single article from pageview api
        """
        query = get_pageview_query_url(s, article.title)

        try:
            response = requests.get(query).json()
        except (requests.RequestException, ValueError):
            response = {}

        if 'items' not in response:
            pageviews = 0
        else:
            pageviews = sum([x['views'] for x in response['items']])

        article.pageviews = pageviews
        return article

    def get(self, s, articles):
        """
        Get pageview counts for a list of articles in parallel
        """
        args_list = [(s, a) for a in articles]
        return thread_function(self.helper, args_list, n_threads=10)
