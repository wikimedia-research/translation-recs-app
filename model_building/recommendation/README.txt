1. Download mulitstream dumps

python download_dumps.py wiki-latest-pages-articles-multistream.xml.bz2 en,fr,es,simple


2. Tokenize the dumps

cd article_tokenization
mvn clean package  # currently buggy

sh run_article_tokenization.sh en enwiki


3. Build LDA Model

LDA_preprocess.py.ipynb
python get_gensim_lda_vectors.py