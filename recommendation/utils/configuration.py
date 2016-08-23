import configparser
from pkg_resources import resource_filename

import recommendation

_config = None


def get_configuration(path, package, name):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    try:
        config.read_file(open(path))
    except IOError:
        config.read_file(open(resource_filename(package, name)))
    return config


def get_config_value(section, key):
    initialize_config()
    return _config.get(section, key)


def get_config_int(section, key):
    initialize_config()
    return _config.getint(section, key)


def get_config_dict(section):
    initialize_config()
    return dict(_config[section])


def initialize_config():
    global _config
    if _config is None:
        _config = get_configuration(recommendation.config_path, recommendation.__name__, recommendation.config_name)
