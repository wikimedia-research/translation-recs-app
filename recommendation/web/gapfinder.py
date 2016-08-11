import json
import requests
from flask import Blueprint, render_template, request

from recommendation.utils import event_logger

gapfinder = Blueprint('gapfinder', __name__, template_folder='templates', static_folder='static', static_url_path='/static/gapfinder')

language_pairs = requests.get('https://cxserver.wikimedia.org/v1/languagepairs').json()


@gapfinder.route('/')
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
