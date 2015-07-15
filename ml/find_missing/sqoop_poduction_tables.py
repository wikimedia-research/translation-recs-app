
import os
db = 'prod_tables'
wikis = ['frwiki', 'plwiki', 'eswiki', 'enwiki'] # 'dewiki', 'eswiki', 'enwiki']
overwrite = True

page_query = """
sqoop import                                                        \
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(wiki)s    \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_XXXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by a.page_id                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                       \
  --create-hive-table                                               \
  --hive-table %(wiki)s_page                                        \
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
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(wiki)s      \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_1XXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by b.rd_from                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                        \
  --create-hive-table                                               \
  --hive-table %(wiki)s_redirect                                          \
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
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(wiki)s      \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_2XXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by a.ll_from                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                        \
  --create-hive-table                                               \
  --hive-table %(wiki)s_langlinks                                         \
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
  --connect jdbc:mysql://analytics-store.eqiad.wmnet/%(wiki)s      \
  --verbose                                                         \
  --target-dir /tmp/$(mktemp -u -p '' -t ${USER}_sqoop_2XXXXX)      \
  --delete-target-dir                                               \
  --username research                                               \
  --password-file /user/ellery/sqoop.password                       \
  --split-by rev_parent_id                                              \
  --hive-import                                                     \
  --hive-database %(db)s                                        \
  --create-hive-table                                               \
  --hive-table %(wiki)s_revision                                         \
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

table_queries = [revision_query] #[page_query, redirect_query, langlinks_query, revision_query]

os.system("export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-amd64")
for wiki in wikis:
    d = {'db':db, 'wiki':wiki}
    for table_query in table_queries:
        os.system( table_query % d )
