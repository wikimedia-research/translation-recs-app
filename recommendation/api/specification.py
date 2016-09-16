import yaml
import pkg_resources
from bravado_core import spec
from bravado_core import marshal
from bravado_core import param
from bravado_core import validate

from recommendation import api

_parsed_spec = None


def initialize_specification():
    global _parsed_spec
    if _parsed_spec is None:
        spec_dict = yaml.load(open(pkg_resources.resource_filename(api.__name__, 'swagger.yml')).read())
        _parsed_spec = spec.Spec.from_dict(spec_dict)


def parse_and_validate_parameters(raw_params):
    initialize_specification()

    clean_params = {}
    for parameter in _parsed_spec.spec_dict['parameters']:
        parameter_spec = _parsed_spec.spec_dict['parameters'][parameter]
        parameter_type = parameter_spec['type']
        parameter_name = parameter_spec['name']
        try:
            value = param.cast_request_param(parameter_type, parameter, raw_params.get(parameter_name))
            validate.validate_schema_object(_parsed_spec, parameter_spec, value)
            clean_params[parameter] = marshal.marshal_schema_object(_parsed_spec, parameter_spec, value)
        except Exception as e:
            raise ValueError(e)

    return clean_params


def marshal_response(recommendations):
    initialize_specification()

    articles_spec = _parsed_spec.spec_dict['definitions']['Articles']
    articles = marshal.marshal_schema_object(_parsed_spec, articles_spec, {'articles': recommendations})
    return articles
