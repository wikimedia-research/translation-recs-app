from flask import Flask, render_template, jsonify, request
import argparse
import json

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

def load_recommenders(data_dir, translation_directions):
    model = {}
    for s, ts in json.load(open(translation_directions)).items():
        model[s] = {}
        tm = TopicModel(data_dir, s)
        model[s]['topic_model'] = tm
        for t in ts:
            model[s][t] = {}
            tr = TranslationRecommender(data_dir, s, t, tm)
            model[s][t]['translation_recommender'] = tr
    print("LOADED MODELS")

    return model
        


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

    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', required = False, type = bool, default = True, help='run in debug mode' )
    parser.add_argument('--data_dir', required = False, default = '../data', help='path to model files' )
    parser.add_argument('--translation_directions', required = False, default = '../test_language_pairs.json', help='path to json file defining language directions' )
    args = parser.parse_args()   
    app.debug = args.debug
    global model
    model = load_recommenders(args.data_dir, args.translation_directions)
    app.run()
