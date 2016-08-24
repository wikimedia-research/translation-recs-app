from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to pytest')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(args=self.pytest_args)
        sys.exit(errno)


setup_parameters = dict(
    name='recommendation',
    version='0.0.1',
    url='https://github.com/wikimedia-research/translation-recs-app',
    license='Apache Software License',
    maintainer='Nathaniel Schaaf',
    maintainer_email='nschaaf@wikimedia.org',
    description='',
    long_description='',
    packages=find_packages(exclude=['test', 'test.*', '*.test']),
    install_requires=['flask',
                      'bravado-core',
                      'PyYAML',
                      'requests',
                      'numpy'],
    package_data={'recommendation.web': ['static/*.*',
                                         'static/i18n/*',
                                         'static/images/*',
                                         'static/suggest-searches/*',
                                         'templates/*'],
                  'recommendation.api': ['swagger.yml']},
    zip_safe=False,
    tests_require=['pytest',
                   'responses'],
    cmdclass={'test': PyTest}
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
