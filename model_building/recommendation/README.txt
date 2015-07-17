1. Download mulitstream dumps

python download_dumps.py wiki-latest-pages-articles-multistream.xml.bz2 en,fr,es,simple


2. Tokenize the dumps

cd article_tokenization
mvn clean package  # currently buggy

sh run_article_tokenization.sh en enwiki


3. Build LDA Model

# Preprocess Dump to get files

spark-submit \
--driver-memory 5g --master yarn --deploy-mode client \
--num-executors 4 --executor-memory 20g --executor-cores 8 \
--queue priority \
/home/ellery/translation-recs-app/model_building/recommendation/lda_preprocess.py \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--lang simple \
--top 100000 

# Build LDA Model: This should happen in spark instead

python /home/ellery/translation-recs-app/model_building/recommendation/get_gensim_lda_vectors.py \
--lang en \
--config /home/ellery/translation-recs-app/translation-recs.ini \
--dim 400