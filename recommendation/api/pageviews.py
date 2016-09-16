import concurrent.futures

from recommendation.api import data_fetcher


def set_pageview_data(source, articles):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(articles)) as executor:
        futures = [executor.submit(_get_and_set_pageview_data, source, article) for article in articles]
        data = [future.result() for future in concurrent.futures.as_completed(futures)]
    return data


def _get_and_set_pageview_data(source, article):
    pageviews = data_fetcher.get_pageviews(source, article.title)
    article.pageviews = pageviews
    return article
