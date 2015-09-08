
For now, just remove disambiguation pages and add last months pageviews:

1. Find Source disambiguation pages

python /home/ellery/translation-recs-app/model_building/rank_missing/get_disambiguation_pages.py \
--s simple \
--config /home/ellery/translation-recs-app/translation-recs.ini 


2. Get Source Pageviews

python /home/ellery/translation-recs-app/model_building/rank_missing/get_pageviews.py \
--s simple \
--min_year 2015 \
--min_month 6 \
--min_day 28\
--config /home/ellery/translation-recs-app/translation-recs.ini 


3. remove disambig from missing file and augment with pageviews


python /home/ellery/translation-recs-app/model_building/rank_missing/rank_missing_by_pageviews.py \
--s en \
--t es \
--config /home/ellery/translation-recs-app/translation-recs.ini 









1. Download Source Language Dumps

python ../recommendation/download_dumps.py wiki-latest-pages-meta-current.xml.bz2  en,fr,es,simple

2. Extract Feautres From Dumps

get_dump_features.ipynb


Where Should Features Come From:

pageviews:
query hive table wmf.page_counts_hourly, try to do this from spark directly
we won't have pageviews of items in other languages


geo_pageviews: same as above


dump_features: i.e. is disambiguation, is_stub, length
use existing script. the problem is that this is no longer parallelizable
you can get stubs and disambiguation pages from category links! 
sqoop category table 
query db and save files for each
get length from tokenized file


Edit Features:
need to sqoop revision table or query db, lets not worry about this for now


Importance Template Label Features:
don't worry about it for now