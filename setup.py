from setuptools import setup, find_packages
import sys

setup_parameters = dict(
    name='recommendation',
    version='0.0.1',
    url='https://github.com/wikimedia-research/translation-recs-app',
    license='Apache Software License',
    maintainer='Wikimedia Research',
    maintainer_email='',
    description='',
    long_description='',
    packages=find_packages(exclude=['test', 'test.*', '*.test']),
    install_requires=['flask',
                      'requests',
                      'futures',
                      'numpy'],
    package_data={'recommendation.web': ['static/*',
                                         'static/i18n/*',
                                         'static/images/*',
                                         'static/suggest-searches/*',
                                         'templates/*'],
                  'recommendation.api': ['swagger.yml']},
    zip_safe=False,
    setup_requires=['pytest-runner'],
    tests_require=['pytest',
                   'responses']
)
if getattr(sys, 'real_prefix', None) is None:
    setup_parameters.update(dict(
        data_files=[('/etc/recommendation', ['recommendation/data/recommendation.wsgi',
                                             'recommendation/data/recommendation.ini',
                                             'recommendation/data/uwsgi.ini'])]
    ))
else:
    setup_parameters['package_data'].update({'recommendation': ['data/*']})

if __name__ == '__main__':
    setup(**setup_parameters)
