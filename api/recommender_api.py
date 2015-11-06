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
def get_recommendations():
    t1 = time.time()
    ret = {'articles': []}

    # required args
    s = request.args.get('s')
    t = request.args.get('t')
    # make sure language codes are valid
    if s not in language_codes or t not in language_codes:
        return json_response(ret)
    if s==t:
        return json_response(ret)


    #optional args with defaults
    n_default = 12
    n = request.args.get('n', n_default)
    try:
        n = min(int(n), 25)
    except:
        n = n_default

    search_default = 'morelike'
    search = request.args.get('search', search_default)
    if search not in ('google', 'wiki', 'morelike'):
        search = search_default


    pageviews = request.args.get('pageviews', 'true')
    if  pageviews == 'false':
        pageviews = False
    else:
        pageviews = True

    article = request.args.get('article')
    if article:
        ret['articles'] = get_seeded_recommendations( s, t, article, n, pageviews, search)
    else:
        ret['articles'] = get_global_recommendations( s, t, n)


    t2 = time.time()
    print('Total:', t2-t1)

    return json_response(ret)


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response



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
