from flask import Flask

from recommendation.api import api
from recommendation.web import gapfinder

app = Flask(__name__)
app.register_blueprint(api.api, url_prefix='/api')
app.register_blueprint(gapfinder.gapfinder)
application = app
