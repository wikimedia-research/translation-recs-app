import configparser
from pkg_resources import resource_filename


def get_configuration(path, package, name):
    config = configparser.ConfigParser()
    try:
        config.read_file(open(path))
    except IOError:
        config.read_file(open(resource_filename(package, name)))
    return config
