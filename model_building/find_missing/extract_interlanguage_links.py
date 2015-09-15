from pyspark import SparkConf, SparkContext
from configparser import SafeConfigParser
import pandas as pd
import argparse
import logging


import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from spark_util import save_rdd, get_parser


import json
import re

"""
Usage: 
spark-submit \
--driver-memory 5g --master yarn --deploy-mode client \
--num-executors 2 --executor-memory 10g --executor-cores 8 \
--queue priority \
/home/ellery/translation-recs-app/model_building/find_missing/extract_interlanguage_links.py \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""



p = re.compile('.*wiki$')


def site_links_to_str(row):
    return '\t'.join(row)

def agg_site_links_to_str(rows):
    s = [rows[0][0]]
    for row in rows:
        s.append(row[1] + '|' + row[2])
    return '\t'.join(s)
        

def get_agg_sitelinks(line):
    
    item = None

    try:
        item = json.loads(line.rstrip('\n,'))
    except:
        return []

    item_id = item['id']
    
    if not item_id.startswith('Q'):
        return []
    links = item['sitelinks']
    
    rows = []
    for k, d in links.items():
        wiki = d['site']
        if p.match(wiki): 
            title = d['title']
            rows.append([item_id, wiki[:-4], title])
    return rows



if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()
    cp = SafeConfigParser()
    cp.read(args.config)


    conf = SparkConf()
    conf.set("spark.app.name", 'finding missing articles')
    sc = SparkContext(conf=conf)

    dumpfile = cp.get('find_missing', 'wikidata_dump')
    

    dump = sc.textFile(dumpfile)
    will = dump.flatMap(get_agg_sitelinks).map(site_links_to_str)
    agg = dump.map(get_agg_sitelinks).filter(lambda x: len(x) > 0).map(agg_site_links_to_str)


    WILLpath = cp.get('find_missing', 'WILL').split('/')[-1]
    aggpath = cp.get('find_missing', 'aggregated_WILL').split('/')[-1]

    os.system('hadoop fs -rm -r ' + WILLpath)
    os.system('hadoop fs -rm -r ' + aggpath)

    will.saveAsTextFile (cp.get('find_missing', 'WILL') )
    agg.saveAsTextFile (cp.get('find_missing', 'aggregated_WILL') )

    

