from operator import add
from pyspark import SparkConf, SparkContext
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
import os
import argparse
from configparser import SafeConfigParser
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from spark_util import get_parser, save_rdd



"""
Usage: 

spark-submit \
--driver-memory 5g --master yarn --deploy-mode client \
--num-executors 4 --executor-memory 20g --executor-cores 8 \
--queue priority \
/home/ellery/translation-recs-app/model_building/recommendation/lda_preprocess.py \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--lang en \
--top 100000 


To run LDA, see wikimedia/missing_articles/src/main/python/get_gensim_lda.py
"""
# set up environment
conf = SparkConf()
conf.set("spark.app.name", 'lda_preprocess')
sc = SparkContext(conf=conf)



def load_articles(language, dump_path, wikidata_mapping_path):
    """
    Right now we have files for enwiki and simple wiki where each line 
    corresponds to the full article text. Tokens seperated by spaces
    """

    # get article to wikidata_item mapping
    wikidata_mapping = sc.textFile(wikidata_mapping_path)\
                       .map(lambda line: line.split('\t'))\
                       .filter(lambda x: x[1] == language)\
                       .map(lambda x: (x[1] + "|" + x[2].replace(' ', '_'), x[0]))

    articles = sc.textFile(dump_path).map(lambda line: line.split('\t'))
    articles = articles.filter(lambda x: len(x) ==4 and len(x[3]) > 0 and len(x[2]) == 0)
    articles = articles.map(lambda x: ('|'.join([language, x[0]]), x[3].split(' ')))
    #print 'Got %d articles pre join' % articles.count()

    # replace page_id with wikidata id
    articles = wikidata_mapping.join(articles)\
                    .map(lambda x: (x[0] + '|' + x[1][0] , x[1][1]))

    #print 'Got %d articles post join' % articles.count()
    return articles


def get_word_id_mapping(articles, min_occurrences = 3, num_tokens = 100000):
    """
    Create a mapping from words to ids. The mapping with contain the "num_tokens" most frequent tokens
    and no token that appears less often than min_occurrences
    """
    words = articles.flatMap(lambda x: x[1])\
    .map(lambda x: (x, 1))\
    .reduceByKey(add)\
    .filter(lambda x: x[1] >= min_occurrences)\
    .top(num_tokens, key=lambda x: x[1])
    
    local_word_map = []
    for w in words:
        t = (w[0], len(local_word_map))
        local_word_map.append(t)
    return dict(local_word_map), sc.parallelize(local_word_map)


def get_banned_words():
    punctuation = set(string.punctuation)
    nltk_stopwords = set(stopwords.words('english'))
    wikimarkup = set(['*nl*', '</ref>', '<ref>', '--', '``', "''", "'s", 'also', 'refer' , '**'])
    banned_words = punctuation.union(nltk_stopwords).union(wikimarkup)
    return banned_words


def clean_article_text(articles, banned_words):
    """

    """
    lower_articles = articles.map(lambda x: (x[0], [w.lower() for w in x[1]]))
    # remove banned words
    clean_articles = lower_articles.map(lambda x: (x[0], [w for w in x[1] if w not in banned_words]))
    # Stem
    def stem_word_list(words):
        stemmer = PorterStemmer()
        return [stemmer.stem(w.lower()) for w in words]
    
    #stemmed_articles = clean_articles.map(lambda x: (x[0], stem_word_list(x[1])))
    return clean_articles #stemmed_articles


def get_term_frequencies(articles):
    """
    Maps each article to a list of (word, freq pairs). Each article now has the from
    (article_id, list((word, freq pairs)))
    """
    def map_tokens_to_frequencies(x):
        doc_id, tokens = x
        from collections import Counter
        frequencies = list(Counter(tokens).items())
        return (doc_id, frequencies)  
    return articles.map(map_tokens_to_frequencies)


def translate_words_to_ids(tf_articles, word_id_map):
    """
    Map (article_id, list((word, freq pairs))) to (article_id, list((word_id, freq pairs)))
    """
    def flatten(x):
        article_id, counts = x
        elems = [(c[0], (article_id, c[1])) for c in counts]
        return elems

    def map_tokens_to_ids(x):
        (token, ((doc_id, count), token_id)) = x
        return (doc_id, (token_id, count))

    return tf_articles.flatMap(flatten).\
    join(word_id_map).\
    map(map_tokens_to_ids).\
    groupByKey()


def main(args):
    cp = SafeConfigParser()
    cp.read(args.config)
    base_dir = os.path.join(cp.get('DEFAULT', 'data_path'), args.lang)
    hadoop_base_dir = os.path.join(cp.get('DEFAULT', 'hadoop_data_path'), args.lang)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    tokenfile = os.path.join(hadoop_base_dir, args.lang+'wiki-plaintexts' )

    # load articles
    tokenized_articles = load_articles(args.lang, tokenfile, cp.get('find_missing', 'WILL'))
    # normalize
    normalized_tokenized_articles = clean_article_text(tokenized_articles, get_banned_words())
    # get word-id maping
    local_word_id_map, word_id_map = get_word_id_mapping(normalized_tokenized_articles, min_occurrences = args.min, num_tokens = args.top)
    # map list of tokens into list of token:count elements
    tf_articles = get_term_frequencies(normalized_tokenized_articles)
    # map list of token:count elements into list of token-id:count
    id_articles = translate_words_to_ids(tf_articles, word_id_map)

    # save dictionary to file: word at line i has id i
    dict_file = os.path.join(base_dir, cp.get('recommendation', 'word2index'))
    with open(dict_file, 'w') as f:
        for word, word_id in sorted(local_word_id_map.items(), key=lambda x:x[1]):
            line = word + '\n'
            f.write(line.encode('utf8'))


    def tuple_to_str(t):
        article, vector = t
        str_vector = [str(e[0]) + ':' + str(e[1]) for e in vector]
        return article + ' ' + str(len(str_vector)) + ' ' + ' '.join(str_vector)
    
    save_rdd(id_articles.map(tuple_to_str), base_dir , hadoop_base_dir, 'articles.pre_blei')
    pre_blei_corpus_file = os.path.join( base_dir, 'articles.pre_blei')
    article2index_file = os.path.join( base_dir, cp.get('recommendation', 'article2index'))
    blei_corpus_file = os.path.join( base_dir, cp.get('recommendation', 'blei_corpus')) 
    print os.system( "cut  -d' ' -f2- %s > %s" % (pre_blei_corpus_file,  blei_corpus_file))
    print os.system( "cut  -d' ' -f1 %s > %s" % (pre_blei_corpus_file, article2index_file))
    os.system("rm " + pre_blei_corpus_file)
    #sc.stop()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='full path to configuration file')
    parser.add_argument('--lang', required = True, help='language of the articles in the corpus')
    parser.add_argument('--min', default = 3, type=int,  help='minimum number of time a word must appear in the corpus')
    parser.add_argument('--top', default = 50000, type=int,  help='include top k tokens in model')
    args = parser.parse_args()
    main(args)
    
