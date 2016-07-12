import concurrent.futures

class Article:
    """
    Struct containing meta-data for an article
    """
    def __init__(self, title):
        self.title = title
        self.wikidata_id = None
        self.rank = None
        self.pageviews = None

def chunk_list(l, chunk_size):
    return [l[i:i+chunk_size] for i in range(0, len(l), chunk_size)]

def thread_function(helper_func, args_list, n_threads = 10):
    with concurrent.futures.ThreadPoolExecutor(n_threads) as executor:
        f = lambda args: helper_func(*args)
        return list(executor.map(f, args_list))
