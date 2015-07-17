1. To Run the library make sure you have the data available locally

The commands below give the data for translating from simple to es. Currently, the ranked_missing_items file is not actually ranked.

rsync  -r  stat1002.eqiad.wmnet:/home/ellery/translation-recs-app/data/simple/doc2topic.mtx /Users/ellerywulczyn/translation-recs-app/data/simple/

rsync  -r  stat1002.eqiad.wmnet:/home/ellery/translation-recs-app/data/simple/article2index.txt /Users/ellerywulczyn/translation-recs-app/data/simple/

rsync  -r  stat1002.eqiad.wmnet:/home/ellery/translation-recs-app/data/simple/es/ranked_missing_items.tsv /Users/ellerywulczyn/translation-recs-app/data/simple/es


2. To see how to use the classes in rec_util.py, see rec_util.ipynb
