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