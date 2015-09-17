from configparser import SafeConfigParser
import pandas as pd
import pymysql
import pandas as pd
import os
import argparse
import logging


"""
Usage: 

python /home/ellery/translation-recs-app/model_building/rank_missing/rank_missing_by_pageviews.py \
--s en \
--t es \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""

logger = logging.getLogger(__name__)


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--t', required = True, help='source language' )
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()   
    cp = SafeConfigParser()
    cp.read(args.config)

    s = args.s
    t = args.t

    sdir = os.path.join(cp.get('DEFAULT', 'data_path'), s)
    
    dis_fname = os.path.join(sdir, cp.get('rank_missing', 'disambiguation'))   
    pv_fname = os.path.join(sdir, cp.get('rank_missing', 'page_views'))  
    missing_fname = os.path.join(sdir,t, cp.get('find_missing', 'missing_items'))

    tdir = os.path.join(sdir, t)
    if not os.path.exists(tdir):
        os.makedirs(tdir)

    ranked_missing_fname = os.path.join(tdir, cp.get('rank_missing', 'ranked_missing_items')) 

    d_dis = pd.read_csv(dis_fname, sep = '\t', encoding = 'utf8')
    d_pv = pd.read_csv(pv_fname, sep = '\t', encoding = 'utf8')
    d_missing = pd.read_csv(missing_fname, sep = '\t', encoding = 'utf8', names = ['id', 'page_title'])

    def underscore(x):
        return x.replace(' ', '_')
        
    d_missing['page_title'] = d_missing['page_title'].astype(str)
    d_missing['page_title'] = d_missing['page_title'].apply(underscore)
    d_ranked = d_missing.merge(d_pv, how = 'inner', on = 'page_title')
    d_dis['is_dis'] = 1
    d_ranked = d_ranked.merge(d_dis, how = 'left', on = 'page_title')
    d_ranked.fillna(0, inplace = True)

    d_ranked = d_ranked[d_ranked['is_dis'] == 0]
    del d_ranked['is_dis']

    d_ranked.sort(['page_views'], ascending = [0], inplace = True)
    d_ranked = d_ranked[d_ranked.page_title != 'Angelsberg']
    d_ranked.to_csv(ranked_missing_fname, sep = '\t', encoding = 'utf8')



