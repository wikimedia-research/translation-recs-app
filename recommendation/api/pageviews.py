import requests
from datetime import datetime
from dateutil import relativedelta
from lib.utils import thread_function

class PageviewGetter():
    """
    Utility Class for getting article pageview counts
    via the pageview API
    """
    def helper(self, s, article):
        """
        Get pageview counts for a single article from pageview api
        """
        start = (datetime.utcnow() - relativedelta.relativedelta(days=1)).strftime('%Y%m%d00')
        stop = (datetime.utcnow() - relativedelta.relativedelta(days=15)).strftime('%Y%m%d00')
        query = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/%s.wikipedia/all-access/user/%s/daily/%s/%s"
        query = query % (s, article.title, stop, start)
        response = requests.get(query).json()

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
        return thread_function(self.helper, args_list, n_threads = 10)