import pymysql
import pandas as pd
import os


# mysql -us52262 -peolaiheiheeviish -hlabsdb1001.eqiad.wmnet

def mysql_to_pandas(dicts):
    dmaster = {}
    for d in dicts:
        for k in d.keys():
            if k not in dmaster:
                dmaster[k] = []
            
            dmaster[k].append(d[k]) 
    return pd.DataFrame(dmaster)

def query_through_tunnel(port,cnf_path, query, params):
    conn = pymysql.connect(host="127.0.0.1", port=port, read_default_file=cnf_path)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return mysql_to_pandas(rows)

def query_db(query, params):
    return query_through_tunnel(8001, "~/.stat3.cnf", query, params)



def get_user_contributions(wiki, user, window = 15):

    query = """
    SELECT page_title, page_id, bytes_added, timestamp, pp_value as wikidata_id
    FROM %(wiki)s.page_props,
    (SELECT page_title, rev_page as page_id, bytes_added, timestamp
    FROM %(wiki)s.page,
    (SELECT rev_page, SUM(bytes_added) as bytes_added, MAX(rev_timestamp) as timestamp FROM
    (SELECT user_revision.rev_page, user_revision.rev_timestamp,  CAST(user_revision.rev_len  AS INt) - CAST(revision.rev_len AS INT)  as bytes_added 
    FROM %(wiki)s.revision,  
    (SELECT rev_page, rev_timestamp, rev_len, rev_parent_id
    FROM %(wiki)s.revision 
    WHERE rev_user_text = '%(user)s'  
    AND rev_minor_edit = 0 
    AND rev_len > 0) user_revision 
    WHERE user_revision.rev_parent_id = revision.rev_id) clean_user_revision 
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
    query = query % {'wiki': wiki, 'user': user}



    return query_db(query, {})