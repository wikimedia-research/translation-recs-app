from ConfigParser import SafeConfigParser
import pandas as pd
import pymysql
import pandas as pd
import os
import argparse


"""
Usage: 

python /home/ellery/translation-recs-app/model_building/rank_missing/get_disambiguation_pages.py \
--s simple \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""





def query_db(query, params):
    conn = pymysql.connect(host = 'analytics-store.eqiad.wmnet', read_default_file="/etc/mysql/conf.d/analytics-research-client.cnf")
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return mysql_to_pandas(rows)


def mysql_to_pandas(dicts):
    dmaster = {}
    for d in dicts:
        for k in d.keys():
            if k not in dmaster:
                dmaster[k] = []
            
            dmaster[k].append(d[k]) 
    return pd.DataFrame(dmaster)


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()   
    cp = SafeConfigParser()
    cp.read(args.config)

    s = args.s

    query = """
    SELECT page_title
    FROM %(db)s.page_props, %(db)s.page
    WHERE pp_page = page_id
    AND page_namespace = 0
    AND page_is_redirect = 0
    AND pp_propname = 'disambiguation'
    """

    dest = os.path.join(cp.get('general', 'local_data_dir'), 'translation-recs-app/data', s)
    if not os.path.exists(dest):
        os.makedirs(dest)

    fname = os.path.join(dest, cp.get('ranking', 'disambiguation'))

    df_dis.to_csv(fname, sep = '\t', encoding = 'utf8', index = False)




