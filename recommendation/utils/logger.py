import logging

from recommendation.utils import configuration
import recommendation


def initialize_logging():
    logging.basicConfig(format=configuration.get_config_value('logging', 'format'),
                        level=logging.WARNING)
    log = logging.getLogger(recommendation.__name__)
    log.setLevel(logging.getLevelName(configuration.get_config_value('logging', 'level')))
