import os
import argparse
import json
from ConfigParser import SafeConfigParser
from datetime import date
from dateutil.relativedelta import relativedelta

#config = /home/ellery/translation-recs-app/translation-recs.ini
# rec_home = /home/ellery/translation-recs-app
# translation_directions = 


"""
Usage

python topic_modeling_pipeline.py \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--translation_directions /home/ellery/translation-recs-app/test_translation_directions.json \
--download_dumps 



"""

def download_dumps(cp, translation_directions):
	script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/recommendation/download_dumps.py')
	langs = ','.join(translation_directions.keys())
	ftype = 'wiki-latest-pages-articles-multistream.xml.bz2'
	os.system('%s %s %s' % (script, ftytpe, langs))

# this file needs to be drier
def tokenize_dumps(cp, translation_directions):
	script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/recommendation/article_tokenization/run_article_tokenization.sh')
	for s in translation_directions.keys():
		os.system('%s %s %s' % (script, s, s+'wiki'))


def lda_preprocess(cp, translation_directions):

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
		os.system(cmd % params)

def lda(cp, translation_directions):

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
		os.system(cmd % params)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='path to config file' )
    parser.add_argument('--translation_directions', required = True)
    parser.add_argument('--download_dumps',action='store_true', default=False)
    parser.add_argument('--tokenize_dumps',action='store_true', default=False)
    parser.add_argument('--lda_preprocess',action='store_true', default=False)
    parser.add_argument('--lda',action='store_true', default=False)


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
    	lda_preprocess

    if args.lda:
    	lda(cp, translation_directions)
    