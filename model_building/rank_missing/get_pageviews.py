from ConfigParser import SafeConfigParser
import pandas as pd
import pymysql
import pandas as pd
import os
import argparse


"""
Usage: 

python /home/ellery/translation-recs-app/model_building/rank_missing/get_pageviews.py \
--s en \
--year 2015 \
--month 6 \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""



def query_hive_ssh(query, file_name):
    cmd =  """hive -e \" """  +query+ """ \" > """ + file_name
    print cmd
    os.system(cmd)
    d = pd.read_csv(file_name,  sep='\t')
    os.system('rm ' + file_name)
    return d


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--year', required = True, help='source language', type = int )
    parser.add_argument('--month', required = True, help='source language', type = int )
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()   
    cp = SafeConfigParser()
    cp.read(args.config)

    s = args.s
    year = args.year
    month = args.month

    query = """
    SET mapred.job.queue.name=priority;
    SELECT page_title, sum(view_count) as page_views
    FROM wmf.pageview_hourly
    WHERE project = '%(s)s.wikipedia'
    AND agent_type = 'user'
    AND year = %(year)s
    AND month = %(month)s
    GROUP BY page_title
    HAVING sum(view_count) > 100;
    """

    params = {
        's': s,
        'year': year,
        'month':  month
    }

    d_pv = query_hive_ssh(query % params, '10k_pv_month')


    dest = os.path.join(cp.get('general', 'local_data_dir'), 'translation-recs-app/data', s)
    if not os.path.exists(dest):
        os.makedirs(dest)

    fname = os.path.join(dest, cp.get('ranking', 'page_views'))

    d_pv.to_csv(fname, sep = '\t', encoding = 'utf8', index = False)



