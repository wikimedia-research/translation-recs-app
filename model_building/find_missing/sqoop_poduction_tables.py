
import os
import sys
from ConfigParser import SafeConfigParser
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--config', required = True, help='path to recommendation file' )
parser.add_argument('--translation_directions', required = True,  help='path to json file defining language directions' )


args = parser.parse_args()
cp = SafeConfigParser()
cp.read(args.config)

os.system("export HIVE_OPTS='-hiveconf mapreduce.job.queuename=priority'")


db = cp.get('DEFAULT', 'hive_db')

with open(args.translation_directions) as f:
  directions = json.load(f)
langs  = set()
langs.add('wikidata')
for k, v in directions.items():
  langs.add(k)
  langs.add(v)


# create the db if it does not exist
create_db = 'CREATE DATABASE IF NOT EXISTS %(db)s;'
params = {'db':db}
cmd =  """hive -e " """ + create_db % params + """ " """
print cmd
os.system( cmd )


# delete all the tables in db that will be refreshed, that already exist
delete_query = "DROP TABLE IF EXISTS %(db)s.%(table)s; "

for lang in langs:
  for s1 in ['wiki_page', 'wiki_redirect', 'wiki_langlinks']:
    for s2 in ['', '_joined']:
      table = lang+s1+s2
      params = {'db':db, 'table': table}
      print cmd
      cmd =  """hive -e " """ + delete_query % params + """ " """
      os.system( cmd )



# sqoop tables into db

page_query = """
sqoop import                                                        \
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(lang)swiki    \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_XXXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by a.page_id                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                       \
  --create-hive-table                                               \
  --hive-table %(lang)swiki_page                                        \
  --query '
SELECT
  a.page_id AS page_id,
  CAST(a.page_title AS CHAR(255) CHARSET utf8) AS page_title
FROM page a
WHERE $CONDITIONS AND page_namespace = 0
'  
"""                                        

redirect_query = """
sqoop import                                                        \
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(lang)swiki      \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_1XXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by b.rd_from                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                        \
  --create-hive-table                                               \
  --hive-table %(lang)swiki_redirect                                          \
  --query '
SELECT
  b.rd_from AS rd_from,
  CAST(b.rd_title AS CHAR(255) CHARSET utf8) AS rd_title
FROM redirect b
WHERE $CONDITIONS AND rd_namespace = 0
'   
"""              

langlinks_query = """
sqoop import                                                      \
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(lang)swiki      \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_2XXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by a.ll_from                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                        \
  --create-hive-table                                               \
  --hive-table %(lang)swiki_langlinks                                         \
  --query '
SELECT
  a.ll_from AS ll_from,
  CAST(a.ll_title AS CHAR(255) CHARSET utf8) AS ll_title,
  CAST(a.ll_lang AS CHAR(20) CHARSET utf8) AS ll_lang
FROM langlinks a
WHERE $CONDITIONS
'
"""


revision_query = """
sqoop import                                                      \
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(lang)swiki      \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_2XXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by rev_parent_id                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                        \
  --create-hive-table                                               \
  --hive-table %(lang)swiki_revision                                         \
  --query '
SELECT
  rev_page,
  rev_user,
  CAST(rev_user_text AS CHAR(255) CHARSET utf8) AS rev_user_text,
  rev_minor_edit,
  rev_deleted,
  rev_len,
  rev_parent_id
FROM revision
WHERE $CONDITIONS
'
"""


os.system("export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-amd64")
for lang in langs:
    d = {'db':db, 'lang':lang}
    for table_query in [page_query, redirect_query, langlinks_query]:
        os.system( table_query % d )


# augment page ids with titles

for lang in langs:
    params = {'db':db, 'lang':lang}

    
    create_query = """
    CREATE TABLE  %(db)s.%(lang)swiki_redirect_joined (
    rd_from STRING,
    rd_to STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    STORED AS TEXTFILE;
    set mapreduce.job.queuename=priority;
    INSERT OVERWRITE TABLE %(db)s.%(lang)swiki_redirect_joined
    SELECT 
    b.page_title as rd_from,
    a.rd_title as rd_to
    FROM %(db)s.%(lang)swiki_redirect a JOIN %(db)s.%(lang)swiki_page b ON( a.rd_from = b.page_id);
    """


    cmd =  """hive -e " """ +create_query % params + """ " """
    print (cmd)
    os.system( cmd )



    create_query = """
    CREATE TABLE  %(db)s.%(lang)swiki_langlinks_joined (
    ll_from STRING,
    ll_to STRING,
    ll_lang STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    STORED AS TEXTFILE;
    set mapreduce.job.queuename=priority;
    INSERT OVERWRITE TABLE %(db)s.%(lang)swiki_langlinks_joined
    SELECT 
    b.page_title as ll_from,
    a.ll_title as ll_to,
    a.ll_lang as ll_lang
    FROM %(db)s.%(lang)swiki_langlinks a JOIN %(db)s.%(lang)swiki_page b ON( a.ll_from = b.page_id);
    """


    cmd =  """hive -e " """ +create_query % params + """ " """
    print (cmd)
    os.system( cmd )



