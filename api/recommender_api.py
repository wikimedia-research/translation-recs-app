import os
import sys
import inspect
import json
import argparse
import requests
import time
from flask import Flask, render_template, jsonify, request

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


from recommendation_lib.api_based_rec import get_seeded_recommendations, get_global_recommendations

app = Flask(__name__)





@app.route('/')
def home():
    return render_template(
        'index.html',
        language_pairs=json.dumps(translation_directions),
        language_codes=json.dumps(language_codes)
    )



@app.route('/api')
def seed_recommendations():
    t1 = time.time()

    if app.debug:
        # add an artificial delay to test UI when in debug mode
        time.sleep(3)

    s = request.args.get('s')
    t = request.args.get('t')
    article = request.args.get('article')
    n = request.args.get('n')

    try:
        n = int(n)
    except:
        n = 10

    ret = {'articles': []}

    # make sure language codes are valid
    if s not in language_codes or t not in language_codes:
        return jsonify(**ret)

    if s==t:
        return jsonify(**ret)

    if article:
        ret['articles'] = get_seeded_recommendations(
            s, t, article, n
        )
    else:
        ret['articles'] = get_global_recommendations(
            s, t, n
        )
    t2 = time.time()
    print('Total:', t2-t1)

    print(jsonify(**ret))
    return jsonify(**ret)


parser = argparse.ArgumentParser()


parser.add_argument(
    '--debug', required=False, action="store_true",
    help='run in debug mode'
)

parser.add_argument(
    '--language_codes', required=False,
    default=os.path.join(parentdir, 'language_codes.json'),
    help='path to json dictionary from language codes to friendly names'
)

args = parser.parse_args()
app.debug = args.debug

language_codes = json.load(open(args.language_codes))
translation_directions = {}
for k1 in language_codes.keys():
    translation_directions[k1] = []
    for k2 in language_codes.keys():
        if k1!=k2:
            translation_directions[k1].append(k2)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
