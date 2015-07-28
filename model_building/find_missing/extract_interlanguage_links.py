from pyspark import SparkConf, SparkContext
from ConfigParser import SafeConfigParser
import pandas as pd
import argparse

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from spark_util import save_rdd, get_parser

import json, re, codecs, sys, HTMLParser


JSON_PATTERN = re.compile(r'^\s*<text xml:space="preserve">(\{&quot;type&quot;:&quot;item&quot;,&quot;id&quot;:&quot;Q.*&quot;,&quot;labels&quot;:.*)</text>')
WIKI_PATTERN = re.compile(r'^(.*)wiki$')
PARSER = HTMLParser.HTMLParser()



"""
Usage: 
spark-submit \
--driver-memory 5g --master yarn --deploy-mode client \
--num-executors 2 --executor-memory 10g --executor-cores 8 \
--queue priority \
/home/ellery/translation-recs-app/model_building/find_missing/extract_interlanguage_links.py \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""



def get_WILL(line):
    match = JSON_PATTERN.match(line)
    if not match:
        return []
    line = PARSER.unescape(match.group(1))
    obj = json.loads(line)
    links = obj['sitelinks']
    if len(links) == 0:
      links = dict()
    ret = []
    for wiki in sorted(links.keys()):
        m = WIKI_PATTERN.match(wiki)
        if m:
            lang = m.group(1)
            ret.append('\t'.join([obj['id'], lang, links[wiki]['title']]))
    return ret


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='path to recommendation file' )
    args = parser.parse_args()
    cp = SafeConfigParser()
    cp.read(args.config)


    conf = SparkConf()
    conf.set("spark.app.name", 'finding missing articles')
    conf.set("spark.akka.frameSize", 30)
    sc = SparkContext(conf=conf)

    dumpfile = cp.get('find_missing', 'wikidata_dump')
    dump = sc.textFile(dumpfile)
    WILLfile = cp.get('find_missing', 'WILL')
    os.system('hadoop fs -rm -r ' + WILLfile)
    dump.flatMap(get_WILL).saveAsTextFile ( WILLfile)
