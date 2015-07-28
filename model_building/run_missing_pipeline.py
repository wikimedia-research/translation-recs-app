import os
import argparse
import json
from ConfigParser import SafeConfigParser


#config = /home/ellery/translation-recs-app/translation-recs.ini
# rec_home = /home/ellery/translation-recs-app
# translation_directions = 


"""
Usage

python run_missing_pipeline.py \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--translation_directions /home/translation-recs-app/language_pairs.json \
--refresh_wills True \
--sqoop_tables False \
--find_missing False

"""

def create_hadoop_dirs(cp):
    os.system('hadoop fs -mkdir %s' % cp.get('DEFAULT', 'hadoop_project_path'))
    os.system('hadoop fs -mkdir %s' % cp.get('DEFAULT', 'hadoop_data_path'))


def get_wikidata_dump(cp):
    wikidata_path  = os.path.join(cp.get('DEFAULT', 'hadoop_data_path'), 'wikidata')
    os.system('hadoop fs -rm -r -f %s' % wikidata_path)
    os.system('hadoop fs -mkdir %s' % wikidata_path)
    os.system("wget -O - http://dumps.wikimedia.org/wikidatawiki/latest/wikidatawiki-latest-pages-articles.xml.bz2 | hadoop fs -put - %s" % wikidata_path)


def get_WILLs(cp):

    script = os.path.join(project_path, 'model_building/find_missing/extract_interlanguage_links.py')
    params = {
        'config': cp.get('DEFAULT', 'config'),
        'script': script
    }
    
    cmd = """
    spark-submit \
    --driver-memory 5g --master yarn --deploy-mode client \
    --num-executors 2 --executor-memory 10g --executor-cores 8 \
    --queue priority \
    %(script)s \
    --config %(config)s 
    """
    os.system(cmd % params)


def sqoop_tables(config, translation_directions_file):
    script = os.path.join(project_path, '/model_building/find_missing/sqoop_production_tables.py')

    params = {
        'translation_directions_file': translation_directions_file,
        'script': script,
        'congig': cp.get('DEFAULT', 'config'),
    }

    cmd = """
    python %(script)s \
    --config %(config)s 
    --translation_directions %(translation_directions_file)s \
    """

    os.system(cmd % params)



def get_missing(config, translation_directions):

    script = os.path.join(project_path, '/model_building/find_missing/get_missing_articles.py')
    
    cmd = """
    spark-submit \
    --driver-memory 5g --master yarn --deploy-mode client \
    --num-executors 2 --executor-memory 10g --executor-cores 8 \
    --queue priority \
    %(script)s \
    --s %(s)s 
    --t %(t)s \
    """

    params = {
        'config': cp.get('DEFAULT', 'config'),
        'script': script,
    }

    for s, ts in translation_directions:
        params['s'] = s
        for t in ts:
            params['t'] = t
            os.system(cmd % params )



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='path to config file' )
    parser.add_argument('--translation_directions', required = True, help='path to json file defining language directions' )
    parser.add_argument('--refresh_wills', default = True, type = bool, help='download the latest wikidatadump and extract WILLs')
    parser.add_argument('--sqoop_tables', default = True, type = bool, help='download the latest wikidatadump and extract WILLs')
    parser.add_argument('--find_missing', default = True, type = bool, help='download the latest wikidatadump and extract WILLs')

    args = parser.parse_args() 
    cp = SafeConfigParser()
    cp.read(args.config)

    with open(args.translation_directions) as f:
        translation_directions = json.load(f)

    if args.refresh_wills:
        create_hadoop_dirs(cp)
        get_wikidata_dump(cp)
        get_WILLs(cp)

    if args.sqoop_tables:
        sqoop_tables(cp, args.translation_directions)

    if args.find_missing:
        get_missing(cp, translation_directions)


