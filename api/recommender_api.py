import os
import sys
import inspect
import json
import argparse
import requests
import time
from flask import Flask, render_template, jsonify, request, Response

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


from recommendation_lib.api_based_rec import get_seeded_recommendations, get_global_recommendations

app = Flask(__name__)


def json_response(dat):
    resp = Response(response=json.dumps(dat),
        status=200, \
        mimetype="application/json")
    return(resp)



@app.route('/')
def home():
    return render_template(
        'index.html',
        language_pairs=json.dumps(translation_directions),
        language_codes=json.dumps(language_codes_map)
    )



@app.route('/api')
def seed_recommendations():
    t1 = time.time()

    if app.debug:
        # add an artificial delay to test UI when in debug mode
        time.sleep(0)

    s = request.args.get('s')
    t = request.args.get('t')
    article = request.args.get('article')
    n = request.args.get('n')

    if request.args.get('pageviews') == 'false':
        pageviews = False
    else:
        pageviews = True

    try:
        n = int(n)
    except:
        n = 10

    ret = {'articles': []}

    # make sure language codes are valid
    if s not in language_codes or t not in language_codes:
        return json_response(ret)

    if s==t:
        return json_response(ret)

    if article:
        ret['articles'] = get_seeded_recommendations(
            s, t, article, n, pageviews
        )
    else:
        ret['articles'] = get_global_recommendations(
            s, t, n
        )
    t2 = time.time()
    print('Total:', t2-t1)

    return json_response(ret)


parser = argparse.ArgumentParser()


parser.add_argument(
    '--debug', required=False, action="store_true",
    help='run in debug mode'
)

parser.add_argument(
    '--language_codes_map', required=False,
    default=os.path.join(parentdir, 'language_codes_map.json'),
    help='path to json dictionary from language codes to friendly names for served language pairs'
)

args = parser.parse_args()
app.debug = args.debug

language_codes =  json.load(open(os.path.join(parentdir, 'language_codes.json')))

language_codes_map = json.load(open(args.language_codes_map))
translation_directions = {}
for s in language_codes_map.keys():
    translation_directions[s] = []
    for t in language_codes_map.keys():
        if s==t:
            continue
        translation_directions[s].append(t)




if __name__ == '__main__':
    app.run(host='0.0.0.0')
