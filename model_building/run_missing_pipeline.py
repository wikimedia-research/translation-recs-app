import os
import argparse
import json
from configparser import SafeConfigParser
from datetime import date
from dateutil.relativedelta import relativedelta

#config = /home/ellery/translation-recs-app/translation-recs.ini
# rec_home = /home/ellery/translation-recs-app
# translation_directions = 


"""
Usage

python run_missing_pipeline.py \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--translation_directions /home/ellery/translation-recs-app/modeled_translation_directions.json \
--download_dump \
--dump_day 20150914 \
--extract_wills \
--sqoop_tables \
--find_missing \
--rank_missing \

"""

def create_hadoop_dirs(cp):
    os.system('hadoop fs -mkdir %s' % cp.get('DEFAULT', 'hadoop_project_path'))
    os.system('hadoop fs -mkdir %s' % cp.get('DEFAULT', 'hadoop_data_path'))


def get_wikidata_dump(cp, day):
    wikidata_path  = os.path.join(cp.get('DEFAULT', 'hadoop_data_path'), 'wikidata')
    os.system('hadoop fs -rm -r -f %s' % wikidata_path)
    os.system('hadoop fs -mkdir %s' % wikidata_path)
    url = 'http://dumps.wikimedia.org/other/wikidata/%s.json.gz' % day
    fname = cp.get('find_missing', 'wikidata_dump')
    ret = os.system("wget -O - %s | hadoop fs -put - %s" % (url, fname))
    assert(ret == 0, 'Loading Wikidata Dump Failed')


def get_WILLs(cp):

    script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/find_missing/extract_interlanguage_links.py')
    params = {
        'config': cp.get('DEFAULT', 'config'),
        'script': script
    }
    

    cmd = """
    spark-submit \
    --driver-memory 5g --master yarn --deploy-mode client \
    --num-executors 4 --executor-memory 10g --executor-cores 4 \
    --queue priority \
    %(script)s \
    --config %(config)s 
    """
    ret = os.system(cmd % params)
    assert(ret == 0, 'Extracting WILLS from Wikidata Dump Failed')


def sqoop_tables(config, translation_directions_file):
    script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/find_missing/sqoop_production_tables.py')

    params = {
        'translation_directions_file': translation_directions_file,
        'script': script,
        'config': cp.get('DEFAULT', 'config'),
    }

    cmd = """
    python %(script)s \
    --config %(config)s \
    --translation_directions %(translation_directions_file)s \
    """
    print (cmd % params)
    ret = os.system(cmd % params)
    assert(ret == 0, 'Sqooping Production Tables Failed')



def get_missing(config, translation_directions):

    script = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/find_missing/get_missing_articles.py')
    
    cmd = """
    spark-submit \
    --driver-memory 5g --master yarn --deploy-mode client \
    --num-executors 2 --executor-memory 10g --executor-cores 8 \
    --queue priority \
    %(script)s \
    --s %(s)s \
    --t %(t)s \
    --config %(config)s
    """

    params = {
        'config': cp.get('DEFAULT', 'config'),
        'script': script,
    }

    for s, ts in translation_directions.items():
        params['s'] = s
        for t in ts:
            params['t'] = t
            print (cmd % params)
            ret = os.system(cmd % params )
            assert(ret == 0, 'get_missing_articles.py failed for s=%s, t=%s' % (s, t))



def rank_missing(config, translation_directions):
    params = { 'config': cp.get('DEFAULT', 'config') }

    for s, ts in translation_directions.items():
        params['s'] = s
    
        cmd = """
        python %(script)s \
        --s %(s)s \
        --config %(config)s
        """
        params['script'] = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/rank_missing/get_disambiguation_pages.py')
        print(cmd % params)
        ret = os.system(cmd % params)
        assert(ret == 0, 'Getting get_disambiguation_pages.py failed s=%s' % s)


        cmd = """
        python %(script)s \
        --s %(s)s \
        --min_year %(min_year)s \
        --min_month %(min_month)s \
        --min_day %(min_day)s\
        --min_views %(min_views)s \
        --config %(config)s
        """

        min_views = {'en': 100, 'simple': 10, 'es': 50, 'fr': 50, 'de': 50}

        params['script'] = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/rank_missing/get_pageviews.py')
        today = date.today()
        lastMonth = today - relativedelta(months=+1)
        params['min_year'] = lastMonth.strftime("%Y")
        params['min_month'] = lastMonth.strftime("%m")
        params['min_day'] = lastMonth.strftime("%d")
        params['min_views'] = min_views.get(s, 10)

        ret = os.system(cmd % params)
        assert(ret == 0, 'get_pageviews.py failed for s=%s' % s)

        for t in ts:
            params['t'] = t
            params['script'] = os.path.join(cp.get('DEFAULT', 'project_path'), 'model_building/rank_missing/rank_missing_by_pageviews.py')
            cmd = """
            python %(script)s \
            --s %(s)s \
            --t %(t)s \
            --config %(config)s 
            """
            ret = os.system(cmd % params)
            assert(ret == 0, 'rank_missing_by_pageviews.py failed for s = %s, t = %s' % (s, t))



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required = True, help='path to config file' )
    parser.add_argument('--translation_directions', required = True)
    parser.add_argument('--download_dump',action='store_true', default=False)
    parser.add_argument('--dump_day', default='20150805' )
    parser.add_argument('--extract_wills',action='store_true', default=False)
    parser.add_argument('--sqoop_tables', action='store_true', default=False)
    parser.add_argument('--find_missing', action='store_true', default=False)
    parser.add_argument('--rank_missing', action='store_true', default=False)

    args = parser.parse_args() 
    cp = SafeConfigParser()
    cp.read(args.config)

    with open(args.translation_directions) as f:
        translation_directions = json.load(f)

    if args.download_dump:
        create_hadoop_dirs(cp)
        get_wikidata_dump(cp, args.dump_day)
    
    if args.extract_wills:
        get_WILLs(cp)

    if args.sqoop_tables:
        sqoop_tables(cp, args.translation_directions)

    if args.find_missing:
        get_missing(cp, translation_directions)

    if args.rank_missing:
        rank_missing(cp, translation_directions)



