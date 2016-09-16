class Article:
    """
    Struct containing meta-data for an article
    """

    def __init__(self, title):
        self.title = title
        self.wikidata_id = None
        self.rank = None
        self.pageviews = None
