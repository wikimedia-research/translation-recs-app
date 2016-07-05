import os
import sys
import inspect
import json
import argparse
import requests
import time
from flask import Flask, render_template, request, Response

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from lib.api_based_rec import get_seeded_recommendations, get_global_recommendations
from lib import event_logger

parser = argparse.ArgumentParser()
parser.add_argument(
    '--debug', required=False, action='store_true',
    help='run in debug mode'
)
args = parser.parse_args()

app = Flask(__name__)
app.debug = args.debug

language_pairs = requests.get('https://cxserver.wikimedia.org/v1/languagepairs').json()


def json_response(dat):
    resp = Response(response=json.dumps(dat),
                    status=200,
                    mimetype='application/json')
    return resp


@app.route('/')
def home():
    s = request.args.get('s')
    t = request.args.get('t')
    seed = request.args.get('seed')
    return render_template(
        'index.html',
        language_pairs=json.dumps(language_pairs),
        s=s,
        t=t,
        seed=seed,
        event_logger_url=event_logger.URL
    )


@app.route('/api')
def get_recommendations():
    t1 = time.time()

    # required args
    s = request.args.get('s')
    t = request.args.get('t')
    # make sure language codes are valid
    ret = {'articles': []}
    if s not in language_pairs['source'] or t not in language_pairs['target']:
        ret['error'] = 'Invalid source or target language'
        return json_response(ret)
    if s == t:
        ret['error'] = 'Source is equal to target language'
        return json_response(ret)

    # optional args with defaults
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
    if pageviews == 'false':
        pageviews = False
    else:
        pageviews = True

    article = request.args.get('article')

    if article:
        recs, error = get_seeded_recommendations(s, t, article, n, pageviews, search)
        event_logger.log_api_request(source=s, target=t, seed=article, search=search)
    else:
        recs, error = get_global_recommendations(s, t, n)
        event_logger.log_api_request(source=s, target=t)

    if recs:
        ret['articles'] = recs
    if error:
        ret['error'] = error

    t2 = time.time()
    print('Total:', t2-t1)

    return json_response(ret)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == '__main__':
    event_logger.URL = 'http://localhost/beacon/event'
    app.run(host='0.0.0.0', debug=True)

