import string
import gensim
import os
import time
import argparse
from scipy.io import mmwrite
from gensim.matutils import MmWriter
from ConfigParser import SafeConfigParser



"""
python /home/ellery/wikimedia/missing_articles/src/main/python/get_gensim_lda_vectors.py \
--dir en_lda_100k \
--config /home/ellery/wikimedia/missing_articles/missing_articles.ini \
--dim 400
"""

def main(args):

    cp = SafeConfigParser()
    cp.read(args.config)
    base_dir = os.path.join(cp.get('general', 'local_data_dir'), args.dir)
    hadoop_base_dir = os.path.join(cp.get('general', 'hadoop_data_dir'), args.dir)


    word2index_file = os.path.join(base_dir, cp.get('LDA', 'word2index'))
    blei_corpus_file = os.path.join(base_dir, cp.get('LDA', 'blei_corpus'))
    doc2topic_file = os.path.join(base_dir, cp.get('LDA', 'doc2topic'))


    dictionary = gensim.corpora.dictionary.Dictionary() 
    id2Token = dict(enumerate(l[:-1] for l in open(word2index_file)))
    dictionary.token2id  = {v: k for k, v in id2Token.items()}
    corpus = gensim.corpora.bleicorpus.BleiCorpus(blei_corpus_file, fname_vocab=word2index_file)


    time1 = time.time()
    model = gensim.models.ldamulticore.LdaMulticore(corpus=corpus,\
                                num_topics=args.dim,\
                                id2word=dictionary,\
                                workers=8,\
                                chunksize=10000,\
                                passes=1,\
                                batch=False,\
                                alpha='symmetric',\
                                eta=None,\
                                decay=0.5,\
                                offset=1.0,\
                                eval_every=10,\
                                iterations=50,\
                                gamma_threshold=0.001)
    time2 = time.time()
    print 'training lda model took %0.3f minutes' % ((time2-time1) / 60.0)
    model.save(os.path.join(base_dir, 'lda_model'))

    time1 = time.time()
    matrix = model[corpus]
    MmWriter.write_corpus(doc2topic_file, matrix)
    time2 = time.time()
    print 'creating lda vectors took %0.3f minutes' % ((time2-time1) / 60.0)

    # move document vectors to hdfs
    #print os.system('hadoop fs -mkdir ' + hadoop_base_dir )
    #print os.system('hadoop fs -put %s %s' % (doc2topic_file, os.path.join(hadoop_base_dir, cp.get('LDA', 'doc2topic')))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', required = True, help='experiment data directory' )
    parser.add_argument('--config', required = True, help='path to configuration file' )
    parser.add_argument('--dim', required = True, type = int, help='vector dimansionality' )

    args = parser.parse_args()
    main(args)

    

