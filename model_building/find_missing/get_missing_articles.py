from pyspark import SparkConf, SparkContext
import codecs
import networkx as nx
from collections import Counter
from pprint import pprint
from ConfigParser import SafeConfigParser
import pandas as pd
import argparse

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from spark_util import get_parser

"""
Usage: 

spark-submit \
--driver-memory 5g --master yarn --deploy-mode client \
--num-executors 2 --executor-memory 10g --executor-cores 8 \
--queue priority \
/home/ellery/translation-recs-app/model_building/find_missing/get_missing_articles.py \
--s simple \
--t es \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""


def create_graph(sc, cp, delim, wd_languages, rd_languages, ill_languages_from, ill_languages_to):
    G = nx.Graph()

    # add wikidata links
    names = ["id", "language_code", "article_name"]
    wikidata_links = sc.textFile(cp.get('find_missing', 'WILL')).map(get_parser(names))\
                    .filter(lambda x: x['language_code'] in wd_languages and x['id'].startswith('Q'))\
                    .map(lambda x: ('wikidata'+ delim + x['id'], x['language_code'] + delim + x['article_name']))         
    G.add_edges_from(wikidata_links.collect())
    print "Got Wikidata Links"
    # add interlanguage links
    prod_tables = cp.get('DEFAULT', 'hive_db_path')

    names = ['ll_from', 'll_to', 'll_lang']
    for ill_lang in ill_languages_from:
        ill = sc.textFile(os.path.join(prod_tables,  ill_lang + 'wiki_langlinks_joined'))\
        .map(lambda x: x.split('\t'))\
        .filter(lambda x: x[2] in ill_languages_to and len(x[1]) > 0 and len(x[0]) > 0)\
        .map(lambda x: (ill_lang + delim + x[0], x[2] + delim + x[1]))
        G.add_edges_from(ill.collect())
        print "Got ILL links for %s" % ill_lang

    # add redirect links
    names = ['rd_from', 'rd_to']
    for rd_lang in rd_languages:
        rd = sc.textFile(os.path.join(prod_tables,  rd_lang + "wiki_redirect_joined"))\
        .map(lambda x: x.split('\t'))\
        .map(lambda x: (rd_lang + delim + x[0], rd_lang + delim + x[1]))
        G.add_edges_from(rd.collect())
        print "got rdd links for %s" % rd_lang
    return G



def test_clustering(G, n, s, t, delim):
    """
    Given a node, find the connected component n is in.
    """
    sub_g = G.subgraph(nx.node_connected_component(G,n ))
    print ("Nodes:")
    pprint(sub_g.nodes())
    print("\nEdges")
    pprint(sub_g.edges())
    print("\nCluster")
    pprint(get_merged_cluster(tumor_g, s, t, delim))
    

def is_subgraph_missing_target_item(g, s, t, delim):
    """
    Given a subgraph, see of it is missing an article in
    the target language
    """
    has_s = False
    has_t = False
    missing_items = {}
    
    for e in g.edges_iter():
        e_dict = {}
        l1, n1 = e[0].split(delim)
        l2, n2 = e[1].split(delim)
        e_dict[l1] = n1
        e_dict[l2] = n2
        
        if 'wikidata' in e_dict and s in e_dict:
            has_s = True
            missing_items[e_dict['wikidata']] = e_dict[s] 
            
        if 'wikidata' in e_dict and t in e_dict:
            has_t = True
                
    if has_s and not has_t:
        return missing_items
    else:
        return {}
    

def get_missing_items(sc, cp, G, s, t, delim, fname):
    """
    Find all items in s missing in t
    """
    cc = nx.connected_component_subgraphs (G)
    missing_items = {}
    for i, g in enumerate(cc):
        missing_items.update(is_subgraph_missing_target_item(g, s, t, delim))

    missing_items_df = pd.DataFrame(missing_items.items())
    missing_items_df.columns = ['id', 'title']
    missing_items_df = missing_items_df[missing_items_df['title'].apply(lambda x: (':' not in x) and (not x.startswith('List')))]

    missing_items_df.to_csv(fname, sep='\t', encoding='utf8', index = False, header = False) 


def get_merged_items(g, s, t, delim):
    """
    """
    merged_items = set()
    has_s = False
    has_t = False
    wikidata_items = set()
    
    for e in g.edges_iter():
        e_dict = {}
        l1, n1 = e[0].split(delim)
        l2, n2 = e[1].split(delim)
        e_dict[l1] = n1
        e_dict[l2] = n2
        
        if 'wikidata' in e_dict and s in e_dict:
            has_s = True
            wikidata_items.add(e_dict['wikidata'])
            merged_items.add(e)
            
        if 'wikidata' in e_dict and t in e_dict:
            has_t = True
            wikidata_items.add(e_dict['wikidata'])
            merged_items.add(e)
        
    if len(wikidata_items) > 1 and has_s and has_t:
        return merged_items, wikidata_items
    else:
        return None, None


def save_merged_items(G, s, t, delim, filename):
    f = open(filename, 'w')
    gs = nx.connected_component_subgraphs (G)
    clusters = []
    for g in gs:
        cluster, items = get_merged_items(g, s, t, delim)
        if cluster:
            cluster = list(cluster)
            cluster = [sorted(edge, reverse=True) for edge in cluster]
            cluster.sort(reverse = True)
            f.write( "\n")
            for edge in cluster:
                line = edge[0] + " " + edge[1] + '\n'
                f.write(line.encode('utf8'))
    f.close()
     


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--t', required = True, help='target language' )
    parser.add_argument('--config', required = True, help='path to recommendation file' )

    delim = '|'

    args = parser.parse_args()
    s = args.s
    t = args.t

    cp = SafeConfigParser()
    cp.read(args.config)


    outerdir = os.path.join(cp.get('DEFAULT', 'data_path'), s)
    if not os.path.exists(outerdir):
        os.makedirs(outerdir)

    innerdir = os.path.join(cp.get('DEFAULT', 'data_path'), s, t)
    if not os.path.exists(innerdir):
        os.makedirs(innerdir)


    wd_languages = set([s, t])
    rd_languages = set([s, t, 'wikidata'])
    ill_languages_from = set([s, t])
    ill_languages_to = set([s, t])

    conf = SparkConf()
    conf.set("spark.app.name", 'finding missing articles')
    conf.set("spark.akka.frameSize", 30)
    sc = SparkContext(conf=conf)


    G = create_graph(sc, cp, delim, wd_languages, rd_languages, ill_languages_from, ill_languages_to)
    print "Got entire Graph"

    get_missing_items(sc, cp, G, s, t, delim, os.path.join(innerdir, cp.get('find_missing', 'missing_items')))
    print "Got missing Items"

    merged_filename = os.path.join(innerdir, cp.get('find_missing', 'merged_items'))
    save_merged_items(G, s, t, delim, merged_filename)
    print "Got clusters"

    sc.stop()
    
    

    



    
