from flask import Flask, render_template, jsonify, request
import pandas as pd

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import json

from recommendation_lib.rec_util import TopicModel, TranslationRecommender
app = Flask(__name__)

DATA_DIR = '../data'
TRANSLATION_DIRECTIONS  = {'simple': ['es', 'fr'], }
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



def get_recommender(s, t):

    if s not in model.keys():
        print ("S DOES NOT EXIST")
        return None

    if t not in model[s]:
        print ("T DOES NOT EXIST")
        return None

    return  model[s][t]['translation_recommender']



@app.route('/')
def personal_recommendations():

    s = request.args.get('s')
    t = request.args.get('t')
    article = request.args.get('article')

    n = request.args.get('article')

    try: 
        n = int(n)
    except:
        n=10

    ret = {'articles': []}
    recommender = get_recommender(s, t)

    if recommender:
        if article:
            ret['articles'] = recommender.get_seeded_recommendations(article, num_recs=n, min_score=0.1)
        else:
            ret['articles'] = recommender.get_global_recommendations(num_recs = n)

    return jsonify(**ret)
    #render_template('translation_recs.html', recs=recs)

   
    
if __name__ == '__main__':
    app.debug = True
    app.run()
