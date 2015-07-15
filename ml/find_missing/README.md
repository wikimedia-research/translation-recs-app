1. Download Wikidata Dump

# from the repo basedir, create wikidata data dir
mkdir data
mkdir data/wikidata
cd data/wikidata

wget http://dumps.wikimedia.org/wikidatawiki/latest/wikidatawiki-latest-pages-articles.xml.bz2

hadoop fs -mkdir translation-recs-app
hadoop fs -mkdir translation-recs-app/data
hadoop fs -mkdir translation-recs-app/data/wikidata
haddop fs -rm -r translation-recs-app/data/wikidata/wikidatawiki-latest-pages-articles.xml

hadoop fs -put wikidatawiki-latest-pages-articles.xml.bz2 translation-recs-app/data/wikidata/wikidatawiki-latest-pages-articles.xml.bz2


2. Extract WILLs from dump

Run extract_interlanguage_links.ipynb
This creates a the file translation-recs-app/data/wikidata/WILLs.tsv in HDFS
TODO: make this into a runable script

3. Sqoop redirect, production tables into hive (db prod_tables) and augment page ids with titles

python sqoop_production_tables.py l1,l2,l3
python join_production_tables.py l1,l2,l3


