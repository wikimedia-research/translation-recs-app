from flask import Flask

from recommendation.api import api
from recommendation.web import gapfinder
from recommendation.utils import logger

logger.initialize_logging()

app = Flask(__name__)
app.register_blueprint(api.api, url_prefix='/api')
app.register_blueprint(gapfinder.gapfinder)
application = app

if __name__ == '__main__':
    application.run(debug=True)
