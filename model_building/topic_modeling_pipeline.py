import os
import argparse
import json
from configparser import SafeConfigParser
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

#config = /home/ellery/translation-recs-app/translation-recs.ini
# rec_home = /home/ellery/translation-recs-app
# translation_directions = 


"""
Usage

python topic_modeling_pipeline.py \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--translation_directions /home/ellery/translation-recs-app/translation_directions.json \
--download_dumps \
--tokenize_dumps \
--lda_preprocess \
--lda 



"""

def download_dumps(cp, translation_directions):
    logger.info('Start: Download all Dumps')
    script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/recommendation/download_dumps.py')
    langs = ','.join(translation_directions.keys())
    ftype = 'wiki-latest-pages-articles-multistream.xml.bz2'
    assert os.system('python %s %s %s' % (script, ftype, langs)) == 0
    logger.info('End: Download all Dumps')

# this file needs to be drier
def tokenize_dumps(cp, translation_directions):
    logger.info('Start: Tokenize all Dumps')
    os.system("export HIVE_OPTS='-hiveconf mapreduce.job.queuename=priority'")
    script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/recommendation/article_tokenization/run_article_tokenization.sh')
    for s in translation_directions.keys():
        fname = os.path.join(cp.get('DEFAULT', 'hadoop_data_path'), s, s+'wiki-plaintexts')
        os.system('hadoop fs -rm -r %s' % fname)
        ret = os.system('sh %s %s %s' % (script, s, s+'wiki'))
        assert ret == 0, 'Error tokenizing s=%s' % s
    logger.info('End: Tokenize all Dumps')


def lda_preprocess(cp, translation_directions):

    logger.info('Start: LDA preprocess')
    script =  os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/recommendation/lda_preprocess.py')
    params = {
        'config': cp.get('DEFAULT', 'config'),
        'script': script
    }

    cmd = """
    spark-submit \
    --driver-memory 5g --master yarn --deploy-mode client \
    --num-executors 4 --executor-memory 20g --executor-cores 8 \
    --queue priority \
    %(script)s \
    --config %(config)s \
    --lang %(s)s \
    --top %(top)s
    """

    for s in translation_directions.keys():
        params['s'] = s
        params['top'] = 100000
        ret = os.system(cmd % params)
        assert ret == 0, 'Error preprossing tokenized dump for s = %s' % s

    logger.info('End: LDA preprocess')

def lda(cp, translation_directions):

    logger.info('Start: LDA')

    script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/recommendation/get_gensim_lda_vectors.py')

    dims  = {'en': 400, 'es': 200, 'fr': 200, 'sw': 100}
    cmd = """
    python %(script)s \
    --lang %(s)s \
    --config %(config)s \
    --dim %(dim)s
    """

    params = {
        'config': cp.get('DEFAULT', 'config'),
        'script': script
    }

    for s in translation_directions.keys():
        params['s'] = s
        params['dim'] = dims.get(s, 100)
        ret = os.system(cmd % params)
        assert ret == 0, 'Error LDA for s = %s' % s

    logger.info('End: LDA')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='path to config file' )
    parser.add_argument('--translation_directions', required = True)
    parser.add_argument('--download_dumps',action='store_true', default=False)
    parser.add_argument('--tokenize_dumps',action='store_true', default=False)
    parser.add_argument('--lda_preprocess',action='store_true', default=False)
    parser.add_argument('--lda',action='store_true', default=False)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('missing_pipeline.log')
    handler.setLevel(logging.INFO)
    shandler = logging.StreamHandler()
    shandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    shandler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(shandler)

    logger.info('###### STARTING TOPIC MODELING PIPELINE ######')

    args = parser.parse_args() 
    cp = SafeConfigParser()
    cp.read(args.config)

    with open(args.translation_directions) as f:
        translation_directions = json.load(f)

    if args.download_dumps:
        download_dumps(cp, translation_directions)

    if args.tokenize_dumps:
        tokenize_dumps(cp, translation_directions)

    if args.lda_preprocess:
        lda_preprocess(cp, translation_directions)

    if args.lda:
        lda(cp, translation_directions)
    