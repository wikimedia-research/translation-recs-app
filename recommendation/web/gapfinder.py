import json
from flask import Blueprint, render_template, request

from recommendation.utils import configuration
from recommendation.utils import language_pairs

gapfinder = Blueprint('gapfinder', __name__, template_folder='templates', static_folder='static',
                      static_url_path='/static/gapfinder')


@gapfinder.route('/')
def home():
    s = request.args.get('s')
    t = request.args.get('t')
    seed = request.args.get('seed')
    pairs = language_pairs.get_language_pairs()
    return render_template(
        'index.html',
        language_pairs=json.dumps(pairs),
        language_to_domain_mapping=json.dumps(language_pairs.get_language_to_domain_mapping()),
        s=s,
        t=t,
        seed=seed,
        event_logger_url=configuration.get_config_value('endpoints', 'event_logger')
    )
