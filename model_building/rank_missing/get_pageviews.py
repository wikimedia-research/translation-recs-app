from configparser import SafeConfigParser
import pandas as pd
import pymysql
import pandas as pd
import os
import argparse
import logging
from datetime import datetime
import dateutil.parser
from dateutil import relativedelta



"""
Usage: 

python /home/ellery/translation-recs-app/model_building/rank_missing/get_pageviews.py \
--s fr \
--min_views 4 \
--start 2015-07-11 \
--stop 2015-08-11 \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""

logger = logging.getLogger(__name__)


def query_hive_ssh(query, file_name):
    cmd =  """hive -e \" """  +query+ """ \" > """ + file_name
    logger.debug (cmd)
    os.system(cmd)

def get_hive_timespan(start, stop, hour = False):
    start = dateutil.parser.parse(start)
    stop = dateutil.parser.parse(stop)
    days = []
    while start <= stop:
        parts = []
        parts.append('year=%d' % start.year)
        parts.append('month=%d' % start.month)
        parts.append('day=%d' % start.day)
        if hour:
            parts.append('hour=%d' % start.hour)
            start += relativedelta.relativedelta(hours=1)
        else:
            start += relativedelta.relativedelta(days=1)
        days.append(' AND '.join(parts))

    condition = '((' + (') OR (').join(days) + '))' 
    return condition



if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--start', required = True, help='' )
    parser.add_argument('--stop', required = True, help='' )
    parser.add_argument('--min_views', default = 1, help='source language' )
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()   
    cp = SafeConfigParser()
    cp.read(args.config)

   
    query = """
    SET mapred.job.queue.name=priority;
    SELECT page_title, sum(view_count) as page_views
    FROM wmf.pageview_hourly
    WHERE project = '%(s)s.wikipedia'
    AND agent_type = 'user'
    AND  %(time)s
    AND page_title not RLIKE '\t'
    GROUP BY page_title
    HAVING sum(view_count) >= %(min_views)s;
    """

    params = {
        's': args.s,
        'min_views': args.min_views,
        'time' : get_hive_timespan(args.start, args.stop)
    }

    print(query % params)

    dest = os.path.join(cp.get('DEFAULT', 'data_path'), args.s)
    if not os.path.exists(dest):
        os.makedirs(dest)

    fname = os.path.join(dest, cp.get('rank_missing', 'page_views'))
    query_hive_ssh(query % params, fname)


    


