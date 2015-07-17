import pandas as pd
import os
from collections import OrderedDict
from scipy.io import mmread
import numpy as np
import scipy



class TopicModel:

    def __init__(self, data_dir, s):
        self.id2index, self.index2id, self.id2sname  = get_recommendation_maps(os.path.join(data_dir,s, 'article2index.txt'))
        self.sname2id = inv_map = {v: k for k, v in self.id2sname.items()}
        topic_matrix_file = os.path.join(data_dir, s, 'doc2topic.mtx')
        print (topic_matrix_file)
        with open(topic_matrix_file, 'rb') as f:
            self.source_topic_matrix = mmread(f).tocsr()



class TranslationRecommender:

    def __init__(self, data_dir, s, t, topic_model):

        self.topic_model = topic_model
        self.missing_df = pd.read_csv(os.path.join(data_dir, s, t, 'ranked_missing_items.tsv'), sep = '\t', encoding = 'utf8')
        missing_set = set(self.missing_df['id'])
        self.missing_topic_matrix = reweight(topic_model, missing_set)


    def get_global_recommendations(self, num_recs=100):
        return list(self.missing_df[:num_recs]['s_title'].values)


    def get_personlized_recommendations(self, interest_vector, num_recs=100, min_score=0.4):
        scores = self.missing_topic_matrix.dot(interest_vector)
        non_zero_indices = np.where(scores > min_score)
        ranking = np.argsort(-scores[non_zero_indices])[:num_recs]
        rec_ids = self.topic_model.index2id[non_zero_indices][ranking]
        #rec_scores = scores[non_zero_indices][ranking]
        #rec_tuples = zip(rec_ids,rec_scores )
        #recs_df = pd.Dataframe(rec_tuples, columns = ['wikidata_id', 'score'])
        return [self.topic_model.id2sname[wdid] for wdid in rec_ids]


    def get_seeded_recommendations(self, article, num_recs=100, min_score=0.4):
        if article not in self.topic_model.sname2id:
            return None
        # get article vector
        article_wdid = self.topic_model.sname2id[article]
        article_index = self.topic_model.id2index[article_wdid]
        article_vector = self.topic_model.source_topic_matrix[article_index].toarray().squeeze()
        return self.get_personlized_recommendations(article_vector, num_recs=num_recs, min_score=min_score)



    def get_user_recommendations(self, contributions_df, num_recs=100, min_score=0.4):

        interest_vector = self.get_user_interest_vector(contributions_df)
        return self.get_personlized_recommendations(interest_vector, num_recs=num_recs, min_score=min_score)
        


    def get_user_interest_vector(self, contribution_df):
        # the editor has not made any contributions
        if contribution_df.shape[0] == 0:
            return np.zeros(self.topic_model.source_topic_matrix.shape[1])
        contribution_df['in_index'] = contribution_df['wikidata_id'].apply(lambda x: x in self.topic_model.id2index)
        contribution_df = contribution_df[contribution_df['in_index'] == True]

        # none of the editors contributions exist in the source wiki
        if contribution_df.shape[0] == 0:
            return np.zeros(self.topic_model.source_topic_matrix.shape[1])

        item_indices = contribution_df['wikidata_id'].apply(lambda x: self.topic_model.id2index[x]).values
        weights = contribution_df['bytes_added'].apply(lambda x: np.log(max(2.0, float(x)))).values
        interest_matrix = self.topic_model.source_topic_matrix[item_indices].toarray()
        interest_vector = interest_matrix.T.dot(weights)
        return interest_vector / np.linalg.norm(interest_vector)


def reweight( topic_model, missing_set):
    M = topic_model.source_topic_matrix
    num_docs = M.shape[0]
    M = M.transpose()
    diagonal = [ 1.0 if topic_model.index2id[i] in missing_set else 0.0 for i in range(num_docs)]
    diagonal = np.array(diagonal)
    assert(np.count_nonzero(np.isnan(diagonal))==0)
    R = scipy.sparse.diags(diagonal, 0)
    M = M*R
    return M.transpose().tocsr()


def get_recommendation_maps(dict_file):
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


 