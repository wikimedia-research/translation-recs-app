#!/bin/bash

# The $WIKI parameter (e.g., zuwiki-20150407) must be passed in as a command-line argument.
export LANG=$1
export WIKI=$2

# Modify these parameters.
# This is where the JAR file with the Mapper code resides.
export TARGET_DIR=$HOME/translation-recs-app/model_building/recommendation/article_tokenization/target
# This is where additional JARs reside.
export LIB_DIR=$HOME/translation-recs-app/model_building/recommendation/lib
# The part of the server logs you want to process.
export IN_FILE=/user/ellery/translation-recs-app/data/$LANG/$WIKI-latest-pages-articles-multistream.xml
# The output directory.
export OUT_DIR=user/ellery/translation-recs-app/data/$LANG/$WIKI-plaintexts

echo "Running hadoop job"
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
    -libjars      $TARGET_DIR/ArticleTokenization-0.0.1-SNAPSHOT-jar-with-dependencies.jar,$LIB_DIR/wikihadoop-0.2.jar \
    -D            mapreduce.output.fileoutputformat.compress=false \
    -D            mapreduce.task.timeout=6000000 \
    -D            org.wikimedia.wikihadoop.previousRevision=false \
    -D            mapreduce.input.fileinputformat.split.minsize=200000000 \
    -inputformat  org.wikimedia.wikihadoop.StreamWikiDumpInputFormat \
    -input        $IN_FILE \
    -output       $OUT_DIR \
    -mapper       org.wikimedia.west1.tokenization.ArticleTokenizerMapper \
    -reducer      "/bin/cat"
