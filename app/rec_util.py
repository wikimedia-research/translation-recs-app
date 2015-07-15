from db_util import query_db
import pandas as pd

def get_recs(target, user = None):
    """
    Returns a list of articles to translate into the target language. If the user is not passed, 
    recs are not personalized
    """
    pass



def get_dummy_recs(target, user = None):
    """
    Returns a list of articles to translate into the target language.
    """
    fname = '../data/en/test/ranked_missing_articles.tsv' 
    df = pd.read_csv(fname, sep = '\t', encoding = 'utf8')
    return  list(df['title_s'])



def get_user_contributions(user, window = 15):

    query = """
    SELECT page_title, page_id, bytes_added, timestamp, pp_value as wikidata_id
    FROM page_props,
    (SELECT page_title, rev_page as page_id, bytes_added, timestamp
    FROM page,
    (SELECT rev_page, SUM(bytes_added) as bytes_added, MAX(rev_timestamp) as timestamp FROM
    (SELECT user_revision.rev_page, user_revision.rev_timestamp,  CAST(user_revision.rev_len  AS INt) - CAST(revision.rev_len AS INT)  as bytes_added \
    FROM revision,  \
    (SELECT rev_page, rev_timestamp, rev_len, rev_parent_id\
    FROM revision \
    WHERE rev_user_text = %(user)s  \
    AND rev_minor_edit = 0 \
    AND rev_len > 0) user_revision \
    WHERE user_revision.rev_parent_id = revision.rev_id) clean_user_revision \
    WHERE bytes_added > 0
    GROUP BY rev_page) grouped_user_revision
    WHERE rev_page = page_id
    AND page_namespace = 0
    AND page_is_redirect = 0
    ORDER BY timestamp DESC
    LIMIT 15) reduced_user_revision
    WHERE page_id = pp_page
    AND pp_propname = 'wikibase_item';
    """

    params = {'user': user}

    return query_db(query. params)


def get_interest_vector(M, id2index, contribution_df):
    if contribution_df.shape[0] == 0:
        return np.zeros(M.shape[1])

    contribution_df['in_index'] = contribution_df['wikidata_id'].apply(lambda x: x in id2index)
    contribution_df = contribution_df[contribution_df['in_index'] == True]
    item_indices = contribution_df['wikidata_id'].apply(lambda x: id2index[x]).values
    weights = contribution_df['bytes_added'].apply(lambda x: np.log(max(2.0, float(x)))).values
    interest_matrix = M[item_indices].toarray()
    interest_vector = interest_matrix.T.dot(weights)
    return interest_vector / np.linalg.norm(interest_vector)



def get_recommendations_helper(MI, MR, id2index, index2id, contributions_df, num_to_rank=1000, min_score=0.4):
    interest_vector = get_interest_vector(MI, id2index, contributions_df)
    scores = MR.dot(interest_vector)
    non_zero_indices = np.where(scores > min_score)
    ranking = np.argsort(-scores[non_zero_indices])[:num_to_rank]
    rec_tuples = zip(index2id[non_zero_indices][ranking], scores[non_zero_indices][ranking])
    recs_df = pd.Dataframe(rec_tuples, columns = ['wikidata_id', 'score'] )
    return recs_df







    