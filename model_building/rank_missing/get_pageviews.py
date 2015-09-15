from configparser import SafeConfigParser
import pandas as pd
import pymysql
import pandas as pd
import os
import argparse
import logging


"""
Usage: 

python /home/ellery/translation-recs-app/model_building/rank_missing/get_pageviews.py \
--s fr \
--min_views 1 \
--min_year 2015 \
--min_month 7 \
--min_day 12 \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""

logger = logging.getLogger(__name__)


def query_hive_ssh(query, file_name):
    cmd =  """hive -e \" """  +query+ """ \" > """ + file_name
    logger.debug (cmd)
    os.system(cmd)
    d = pd.read_csv(file_name,  sep='\t')
    os.system('rm ' + file_name)
    return d


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--min_year', required = True, help='' )
    parser.add_argument('--min_month', required = True, help='' )
    parser.add_argument('--min_day', required = True, help='s' )
    parser.add_argument('--min_views', default = 10, help='source language' )
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()   
    cp = SafeConfigParser()
    cp.read(args.config)

    s = args.s
    year = args.min_year
    month = args.min_month
    day = args.min_day
    min_views = args.min_views

    query = """
    SET mapred.job.queue.name=priority;
    SELECT page_title, sum(view_count) as page_views
    FROM wmf.pageview_hourly
    WHERE project = '%(s)s.wikipedia'
    AND agent_type = 'user'
    AND year >= %(year)s
    AND month >= %(month)s
    AND day >= %(month)s
    GROUP BY page_title
    HAVING sum(view_count) >= %(min_views)s;
    """

    params = {
        's': s,
        'year': year,
        'month':  month,
        'day': day,
        'min_views': min_views,
    }

    d_pv = query_hive_ssh(query % params, '10k_pv_month')


    dest = os.path.join(cp.get('DEFAULT', 'data_path'), s)
    if not os.path.exists(dest):
        os.makedirs(dest)

    fname = os.path.join(dest, cp.get('rank_missing', 'page_views'))

    d_pv.to_csv(fname, sep = '\t', encoding = 'utf8', index = False)



