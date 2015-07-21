from flask import Flask, render_template, jsonify
import pandas as pd

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import json

from recommendation_lib.rec_util import TopicModel, TranslationRecommender
app = Flask(__name__)

DATA_DIR = '../data'
TRANSLATION_DIRECTIONS  = {'simple': ['es'], }
                            #'en': ['es', 'fr', 'simple'] }

def load_recommenders():
    model = {}
    for s, ts in TRANSLATION_DIRECTIONS.items():
        model[s] = {}
        tm = TopicModel(DATA_DIR, s)
        model[s]['topic_model'] = tm
        for t in ts:
            model[s][t] = {}
            tr = TranslationRecommender(DATA_DIR, s, t, tm)
            model[s][t]['translation_recommender'] = tr
    print("LOADING MODELS")

    return model
        
model = load_recommenders()

@app.route('/')
def home():
    return 'Contribution Recommendations'

    
@app.route('/<s>/<t>/<article>')
def translation_recommendations(s, t, article = None):

    ret = {'articles': {}}
    
    if s not in model.keys():
        print ("S NOT EXIST")
        return jsonify(**ret)


    if t not in model[s]:
        print ("T NOT EXIST")
        return jsonify(**ret)
    

    print(article)

    recommender = model[s][t]['translation_recommender']

    if not article:
        recs = recommender.get_global_recommendations(num_recs = 10)
    else:
        recs = recommender.get_seeded_recommendations(article, num_recs=10, min_score=0.1)


    ret['articles'] = recs
    return jsonify(**ret)
    #render_template('translation_recs.html', recs=recs)

   
    
if __name__ == '__main__':
    app.debug = True
    app.run()
