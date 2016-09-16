import logging

from recommendation.api import data_fetcher

log = logging.getLogger(__name__)


def filter_by_missing(source, target, candidates):
    """
    Filters out which articles from source already exist in target
    using Wikidata sitelinks
    """
    titles = [article.title for article in candidates]
    title_id_dict = data_fetcher.get_wikidata_sitelinks(source, target, titles)

    filtered_articles = []

    for article in candidates:
        if article.title in title_id_dict:
            # TODO: change this side-effect to be more explicit / non-stateful
            article.wikidata_id = title_id_dict[article.title]
            filtered_articles.append(article)

    return filtered_articles


def filter_by_disambiguation(source, candidates):
    """
    Filters out disambiguation pages
    """
    titles = [article.title for article in candidates]
    disambiguation_pages = data_fetcher.get_disambiguation_pages(source, titles)
    return [article for article in candidates if article.title not in disambiguation_pages]


def filter_by_title(candidates):
    """
    Filters articles based on the properties of the title
    """
    return [article for article in candidates if ':' not in article.title and not article.title.startswith('List')]


def apply_filters(source, target, candidates, count):
    log.debug('Number of candidates: %d', len(candidates))
    candidates = filter_by_title(candidates)
    log.debug('Number of candidates after title: %d', len(candidates))
    candidates = filter_by_missing(source, target, candidates)
    log.debug('Number of candidates after missing: %d', len(candidates))
    candidates = filter_by_disambiguation(source, candidates)
    log.debug('Number of candidates after disambiguation: %d', len(candidates))

    return candidates[:count]
