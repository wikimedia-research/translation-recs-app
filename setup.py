from setuptools import setup, find_packages
from pip.req import parse_requirements
import sys

setup_parameters = dict(
    name='recommendation',
    version='0.0.1',
    maintainer='',
    maintainer_email='',
    url='',
    description='',
    long_description='',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[str(r.req) for r in parse_requirements('requirements.txt', session=False)],
    package_data={'': ['static/*', 'templates/*']},
    zip_safe=False
)
if getattr(sys, 'real_prefix', None) is None:
    setup_parameters.update(dict(
        data_files=[('/etc/recommendation', ['recommendation/data/recommendation.wsgi',
                                             'recommendation/data/gapfinder.ini'])]
    ))
else:
    setup_parameters['package_data'].update({'recommendation': ['data/*']})

import json
print(json.dumps(setup_parameters, indent=2))

if __name__ == '__main__':
    setup(**setup_parameters)
