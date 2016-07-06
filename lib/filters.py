import itertools
import requests
import concurrent.futures


class MissingFilter():

    def query_wikidata_sitelinks(self, s, titles):

        api = 'https://www.wikidata.org/w/api.php'

        params = {
                    'action': 'wbgetentities',
                    'sites': '%swiki' % s,
                    'titles': '|'.join(titles),
                    'props': 'sitelinks/urls',
                    'format': 'json',
                    }
        response = requests.get(api, params=params)
            
        if response:
            return response.json()
        else:
            print('Bad Wikidata API response')
            return {}


    def parse_wikidata_sitelinks_data(self, s, t, data):

        title_id_dict = {}
        swiki = '%swiki' % s
        twiki = '%swiki' % t

        if 'entities' not in data:
            print ('None of the titles have a Wikidata Item')
            return title_id_dict

        for k, v in data['entities'].items():
            if 'sitelinks' in v:
                if swiki in v['sitelinks'] and twiki not in v['sitelinks']:
                    title = v['sitelinks'][swiki]['title'].replace(' ', '_')
                    title_id_dict[title] = k

        if len(title_id_dict) == 0:
            print("None of the source articles missing in the target")

        return title_id_dict


    def filter_subset(self, s, t, articles):

        d = {a.title:a for a in articles}
        titles = [a.title for a in articles]

        data = self.query_wikidata_sitelinks(s, titles)
        title_id_dict =  self.parse_wikidata_sitelinks_data(s, t, data)

        filtered_articles = []

        for title, wikidata_id in title_id_dict.items():
            article = d[title]
            article.wikidata_id = wikidata_id
            filtered_articles.append(article)

        return filtered_articles


    def filter(self, s, t, articles):

        with concurrent.futures.ThreadPoolExecutor(10) as executor:
            chunk_size = 10
            chunks = [articles[i:i+chunk_size] for i in range(0, len(articles), chunk_size)]
            f = lambda args: self.filter_subset(*args)
            args_list = [(s, t, chunk) for chunk in chunks]
            results = executor.map(f, args_list)
            return list(itertools.chain.from_iterable(list(results)))



class DisambiguationFilter():

    def query_disambiguation_pages(self, s, titles):

        api = 'https://%s.wikipedia.org/w/api.php' % s

        params = {
                    'action': 'query',
                    'prop': 'pageprops',
                    'pprop': 'disambiguation',
                    'titles': '|'.join(titles),
                    'format': 'json',
                    }
        response = requests.get(api, params=params)
            
        if response:
            return response.json()
        else:
            print('Bad Disambiguation API response')
            return {}


    def parse_disambiguation_page_data(self, data):

        disambiguation_pages = set()

        if 'query' not in data or 'pages' not in data['query']:
            print('Error finding disambiguation pages')
            return set()

        for k,v in data['query']['pages'].items():
            if 'pageprops' in v and 'disambiguation' in v['pageprops']:
                title = v['title'].replace(' ', '_')
                disambiguation_pages.add(title)

        return disambiguation_pages

    def filter(self, s, articles):
        titles = [a.title for a in articles]
        data = self.query_disambiguation_pages(s, titles)
        disambiguation_pages = self.parse_disambiguation_page_data(data)
        return [a for a in articles if a.title not in disambiguation_pages]



def apply_filters_chunkwise(s, t, candidates, n_recs, step = 50):
    filtered_candidates = []
    indices = list(zip(range(0, len(candidates) - step, step), range(step, len(candidates), step)))
    
    # filter candidates in chunks, stop once we reach n_recs
    for start, stop in indices:
        print('Filtering Next Chunk')
        subset = candidates[start:stop]
        subset = MissingFilter().filter(s, t, subset)
        subset = DisambiguationFilter().filter(s, subset)
        filtered_candidates += subset
        if len(filtered_candidates) >= n_recs:
            break

    return filtered_candidates
