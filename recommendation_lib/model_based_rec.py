import pandas as pd
import os
from collections import OrderedDict
from scipy.io import mmread
import numpy as np
import scipy
from sklearn.preprocessing import normalize
import requests
from google import search
from api_based_rec import wiki_search, google_search




def load_recommenders(data_dir, translation_directions, language_codes, alg):
    model = {}
    directions = json.load(open(translation_directions))
    model['directions'] = directions
    model['codes'] = json.load(open(language_codes))

    if alg == 'lda':
        for s, ts in directions.items():
            model[s] = {}
            print('Loading Topic Model for: ', s)
            tm = TopicModel(data_dir, s)
            model[s]['topic_model'] = tm
            for t in ts:
                model[s][t] = {}
                print('Loading Recommender for: ', t)
                tr = LDATranslationRecommender(data_dir, s, t, tm)
                model[s][t]['translation_recommender'] = tr
        print("LOADED MODELS")
    else:
        for s, ts in directions.items():
            print('source', s)
            model[s] = {}
            for t in ts:

                print('target', t)
                model[s][t] = {}
                tr = SearchTranslationRecommender(data_dir, s, t)
                model[s][t]['translation_recommender'] = tr

    return model


def get_recommender(s, t):

    if s not in model.keys():
        print ("S DOES NOT EXIST")
        return None

    if t not in model[s]:
        print ("T DOES NOT EXIST")
        return None

    return model[s][t]['translation_recommender']



class TranslationRecommender:
    def __init__(self, data_dir, s, t,):
        self.data_dir = data_dir
        self.s = s
        self.t = t
        self.missing_df = pd.read_csv(os.path.join(data_dir, s, t, 'ranked_missing_items.tsv'), sep = '\t', encoding = 'utf8')
        self.missing_df['page_title'] = self.missing_df['page_title'].astype(str)
        self.missing_df['page_title'] = self.missing_df['page_title'].apply(lambda x: x.replace(' ', '_'))
        self.missing_df.index = self.missing_df['page_title']
        del self.missing_df['page_title']

    def get_global_recommendations(self, num_recs=100):
        names = list(self.missing_df[:num_recs].index.values)
        return [{'title': name,
                 'pageviews': int(self.missing_df.ix[name]['page_views']),
                 'wikidata_id': self.missing_df.ix[name]['id']}
                for name in names] 

    def get_seeded_recommendations(self, article, num_recs=100):
        pass


class SearchTranslationRecommender(TranslationRecommender):
    def __init__(self, data_dir, s, t):
        TranslationRecommender.__init__(self, data_dir, s, t)

    def get_seeded_recommendations(self, article, num_recs=10):

        try:
            results = google_search(self.s, article, num_recs * 3)
            print(results)
        except:
            print('Could not use google search')
            results = wiki_search(self.s, article, num_recs * 3)

        
        results = [r for r in results if r in self.missing_df.index]
        results =  [{'title': name,
                 'pageviews': int(self.missing_df.ix[name]['page_views']),
                 'wikidata_id': self.missing_df.ix[name]['id']}
                for name in results][:num_recs]

        results.sort(key = lambda x: x['pageviews'], reverse=True)
        return results

        

class LDATranslationRecommender(TranslationRecommender):

    def __init__(self, data_dir, s, t, topic_model):
        TranslationRecommender.__init__(self, data_dir, s, t)
        self.topic_model = topic_model
        self.missing_ids = set(self.missing_df['id'])
        self.missing_topic_matrix = self.reweight(self.topic_model, self.missing_ids)


    def reweight(self, topic_model, missing_set):
        M = topic_model.source_topic_matrix
        num_docs = M.shape[0]
        M = M.transpose()
        diagonal = [ 1.0 if topic_model.index2id[i] in missing_set else 0.0 for i in range(num_docs)]
        diagonal = np.array(diagonal)
        assert(np.count_nonzero(np.isnan(diagonal))==0)
        R = scipy.sparse.diags(diagonal, 0)
        M = M*R
        return M.transpose().tocsr()


    def get_personlized_recommendations(self, interest_vector, num_recs=100, min_score=0.4):
        scores = self.missing_topic_matrix.dot(interest_vector)
        non_zero_indices = np.where(scores > min_score)
        ranking = np.argsort(-scores[non_zero_indices])[:num_recs]
        rec_ids = self.topic_model.index2id[non_zero_indices][ranking]
        names = [self.topic_model.id2sname[wdid] for wdid in rec_ids]
        return [{'title': name,
                 'pageviews': int(self.missing_df.ix[name]['page_views']),
                 'wikidata_id': self.missing_df.ix[name]['id']}
                for name in names]


    def get_seeded_recommendations(self, article, num_recs=100, min_score=0.4):
        article = self.normalize_title(self.s, article)
        if article not in self.topic_model.sname2id:
            return []
        # get article vector
        article_wdid = self.topic_model.sname2id[article]
        article_index = self.topic_model.id2index[article_wdid]
        article_vector = self.topic_model.source_topic_matrix[article_index].toarray().squeeze()
        return self.get_personlized_recommendations(article_vector, num_recs=num_recs, min_score=min_score)


    def normalize_title(s, title):
        mw_api = 'https://%s.wikipedia.org/w/api.php' % s
        params = {
            'action': 'query', 'format': 'json', 'titles': title, 'redirects': ''
        }
        response = requests.get(mw_api, params=params).json()['query']
        page_id, page_info = list(response['pages'].items())[0]

        if page_id == '-1':
            return title
        else:
            return page_info['title'].replace(' ', '_')

    def get_user_recommendations(self, contributions_df, num_recs=100, min_score=0.1):

        interest_vector = self.get_user_interest_vector(contributions_df)
        return self.get_personlized_recommendations(interest_vector, num_recs=num_recs, min_score=min_score)
        


    def get_user_interest_vector(self, contribution_df):
        # the editor has not made any contributions
        if contribution_df.shape[0] == 0:
            return np.zeros(self.topic_model.source_topic_matrix.shape[1])

        try:
            contribution_df['in_index'] = contribution_df['wikidata_id'].apply(lambda x: x in self.topic_model.id2index)
        except:
            print ('conversion to unicode already ahppened')
        contribution_df = contribution_df[contribution_df['in_index'] == True]

        # none of the editors contributions exist in the source wiki
        if contribution_df.shape[0] == 0:
            return np.zeros(self.topic_model.source_topic_matrix.shape[1])

        item_indices = contribution_df['wikidata_id'].apply(lambda x: self.topic_model.id2index[x]).values
        weights = contribution_df['bytes_added'].apply(lambda x: np.log(max(2.0, float(x)))).values
        interest_matrix = self.topic_model.source_topic_matrix[item_indices].toarray()
        interest_vector = interest_matrix.T.dot(weights)
        return interest_vector / np.linalg.norm(interest_vector)


class TopicModel:

    def __init__(self, data_dir, s):
        self.id2index, self.index2id, self.id2sname  = self.load_topic_model_maps(os.path.join(data_dir,s, 'article2index.txt'))
        self.sname2id = inv_map = {v: k for k, v in self.id2sname.items()}
        topic_matrix_file = os.path.join(data_dir, s, 'doc2topic.mtx')
        with open(topic_matrix_file, 'rb') as f:
            self.source_topic_matrix =  normalize(mmread(f).tocsr(), norm='l2', axis=1)


    def load_topic_model_maps(self, dict_file):
        id2index = {}
        index2id = []
        id2name = {}
        
        with open(dict_file) as f:
            for index, identifier in enumerate(f):
                identifiers = identifier.strip().split('|')
                item_id  = identifiers[2]
                name = identifiers[1]
                
                id2name[item_id] = name
                id2index[item_id] = index
                index2id.append(item_id)
        return id2index, np.array(index2id), id2name 




  


 