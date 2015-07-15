from pyspark import SparkConf, SparkContext
import argparse
import os
import codecs
import networkx as nx
from collections import Counter
from pprint import pprint
from ConfigParser import SafeConfigParser
from util import get_parser
import pandas as pd
from util import get_parser, save_rdd


"""
Usage: 

spark-submit \
--driver-memory 5g --master yarn --deploy-mode client \
--num-executors 2 --executor-memory 10g --executor-cores 8 \
--queue priority \
/home/ellery/translation-recs-app/ml/sfind_missing/get_missing_articles.py \
--s en \
--t fr \
--config /home/ellery/translation-recs-app/translation-recs.ini 
"""


def create_graph(sc, cp, delim, wd_languages, rd_languages, ill_languages_from, ill_languages_to):
    G = nx.Graph()

    # add wikidata links
    names = ["id", "language_code", "article_name"]
    wikidata_links = sc.textFile(cp.get('general', 'id2article')).map(get_parser(names))\
                    .filter(lambda x: x['language_code'] in wd_languages and x['id'].startswith('Q'))\
                    .map(lambda x: ('wikidata'+ delim + x['id'], x['language_code'] + delim + x['article_name']))         
    G.add_edges_from(wikidata_links.collect())
    print "Got Wikidata Links"
    # add interlanguage links
    prod_tables = cp.get('general', 'prod_tables')

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
    

def get_missing_items(sc, cp, G, s, t, r, delim, exp_dir, n = 100):
    """
    Find all items in s missing in t
    """
    cc = nx.connected_component_subgraphs (G)
    missing_items = {}
    for i, g in enumerate(cc):
        missing_items.update(is_subgraph_missing_target_item(g, s, t, delim))
<<<<<<< HEAD
<<<<<<< HEAD

    missing_items_df = pd.DataFrame(missing_items.items())
    missing_items_df.columns = ['id', 'title']
    missing_items_df = missing_items_df[missing_items_df['title'].apply(lambda x: (':' not in x) and (not x.startswith('List')))]

    pageviews = sc.textFile(cp.get('general', 'pageviews'))\
    .map(lambda x: x.split('\t'))\
    .filter(lambda x: x[1] == s)\
    .map(lambda x: (x[0], int(x[3]))).collect()
    pageviews_df = pd.DataFrame(pageviews)
    pageviews_df.columns = ['id', 'n']

    missing_items_df = missing_items_df.merge(pageviews_df, on='id')
    missing_items_df = missing_items_df.sort('n', ascending = False)
    fname = os.path.join(cp.get('general', 'local_data_dir'), exp_dir, cp.get('missing', 'missing_items'))
    missing_items_df.to_csv(fname, sep='\t', encoding='utf8', index = False, header = False) 
=======
    
    print("Got %d missing items" % len(missing_items))
    # HACK: remove lists articles with colon :
    missing_items = sc.parallelize(missing_items.iteritems())\
                    .filter(lambda x: ':' not in x[1])\
                    .filter(lambda x: not x[1].startswith('List'))
=======
>>>>>>> f8f312aa183d1112b05d8a0b0d4e0430f87e5761

    missing_items_df = pd.DataFrame(missing_items.items())
    missing_items_df.columns = ['id', 'title']
    missing_items_df = missing_items_df[missing_items_df['title'].apply(lambda x: (':' not in x) and (not x.startswith('List')))]

    pageviews = sc.textFile(cp.get('general', 'pageviews'))\
    .map(lambda x: x.split('\t'))\
    .filter(lambda x: x[1] == s)\
    .map(lambda x: (x[0], int(x[3]))).collect()
    pageviews_df = pd.DataFrame(pageviews)
    pageviews_df.columns = ['id', 'n']

<<<<<<< HEAD
    ranked_missing_items = missing_items.sortBy(lambda x: -x[1][1])

    print("Got %d missing items after ranking" % ranked_missing_items.count())

    def tuple_to_str(t):
        item_id, (item_name, n) = t
        line = item_id + '\t' + item_name + '\t' + str(n) 
        return line

    str_ranked_missing_items = ranked_missing_items.map(tuple_to_str)
    base_dir = os.path.join(cp.get('general', 'local_data_dir'), exp_dir)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    hadoop_base_dir = os.path.join(cp.get('general', 'hadoop_data_dir'), exp_dir)
    save_rdd (str_ranked_missing_items,  base_dir , hadoop_base_dir, cp.get('missing', 'ranked_missing_items'))
    
>>>>>>> 596f5a4f5162be2053b696be271051f3763d056e
=======
    missing_items_df = missing_items_df.merge(pageviews_df, on='id')
    missing_items_df = missing_items_df.sort('n', ascending = False)
    fname = os.path.join(cp.get('general', 'local_data_dir'), exp_dir, cp.get('missing', 'missing_items'))
    missing_items_df.to_csv(fname, sep='\t', encoding='utf8', index = False, header = False) 
>>>>>>> f8f312aa183d1112b05d8a0b0d4e0430f87e5761


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
    parser.add_argument('--dir', required = True, help='experiment dir' )
    parser.add_argument('--s', required = True, help='source language' )
    parser.add_argument('--t', required = True, help='target language' )
    parser.add_argument('--r', required = True, help='recommendation language' )
    parser.add_argument('--config', required = True, help='path to recommendation file' )


    args = parser.parse_args()
    exp_dir = args.dir
    s = args.s
    t = args.t
    r = args.r

    cp = SafeConfigParser()
    cp.read(args.config)
<<<<<<< HEAD

    delim = '|'

=======

    delim = '|'

>>>>>>> 596f5a4f5162be2053b696be271051f3763d056e
    wd_languages = set([s, t, r])
    rd_languages = set([s, t, r, 'wikidata'])
    ill_languages_from = set([s, t, r])
    ill_languages_to = set([s, t, r])

    conf = SparkConf()
    conf.set("spark.app.name", 'finding missing articles')
<<<<<<< HEAD
<<<<<<< HEAD
    conf.set("spark.akka.frameSize", 30)
=======
>>>>>>> 596f5a4f5162be2053b696be271051f3763d056e
=======
    conf.set("spark.akka.frameSize", 30)
>>>>>>> f8f312aa183d1112b05d8a0b0d4e0430f87e5761
    sc = SparkContext(conf=conf)


    G = create_graph(sc, cp, delim, wd_languages, rd_languages, ill_languages_from, ill_languages_to)
    print "Got entire Graph"
    get_missing_items(sc, cp, G, s, t, r, delim, exp_dir, n = 10000)
    print "Got missing Items"
<<<<<<< HEAD
<<<<<<< HEAD
=======


>>>>>>> 596f5a4f5162be2053b696be271051f3763d056e
=======
>>>>>>> f8f312aa183d1112b05d8a0b0d4e0430f87e5761
    merged_filename = os.path.join(cp.get('general', 'local_data_dir'), exp_dir, cp.get('missing', 'merged_items'))
    save_merged_items(G, s, t, delim, merged_filename)
    print "Got clusters"

    sc.stop()
    
    

    



    
