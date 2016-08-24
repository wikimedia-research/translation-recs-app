#!/usr/bin/env python3

from subprocess import check_call
from datetime import datetime
import textwrap
import shutil
import os
import imp
import sys


def build(version_suffix=None):
    try:
        setup = imp.load_source('setup', 'setup.py')
    except IOError:
        raise RuntimeError('setup.py not found')
    except SystemExit:
        raise RuntimeError('setup.py is trying to execute')

    # Get values from the setup.py
    params = setup.setup_parameters

    maintainer = params['maintainer']
    maintainer_email = params['maintainer_email']
    description = params['description']
    long_description = params['long_description']

    # Prepend 'python3-' to the package name
    package_name = 'python3-' + params['name']

    version = params['version']
    if version_suffix is None:
        version = get_dev_version(version)
    else:
        version += version_suffix

    # These environment variables are read by debchange
    os.environ['DEBFULLNAME'] = maintainer
    os.environ['DEBEMAIL'] = maintainer_email

    # Copy everything into a clean build directory
    shutil.rmtree('deb_build_dir', ignore_errors=True)
    shutil.copytree('.', 'deb_build_dir', ignore=shutil.ignore_patterns('.*', '*.deb', '*.build', '*.egg-info', '*.pyc'))
    os.chdir('deb_build_dir')

    # Inject values from setup.py into the control file
    with open('debian/control', 'r') as f:
        control = f.read()

    control = control.format(maintainer=maintainer,
                             maintainer_email=maintainer_email,
                             package_name=package_name,
                             description=description,
                             long_description=wrap_description(long_description))

    with open('debian/control', 'w') as f:
        f.write(control)

    # Generate the changelog
    check_call(['debchange',
                '--create',
                '--package',
                package_name,
                '--newversion',
                version,
                '--distribution',
                'unstable',
                '--force-distribution',
                '--preserve',
                'Please contact the maintainer for details about this software.'])

    check_call(['debuild', '--no-tgz-check', '-us', '-uc', '-b'])

    os.chdir('..')


def get_dev_version(version):
    return '{}~{}-1'.format(version, datetime.now().strftime('%Y%m%d%H%M%S'))


def wrap_description(description):
    wrapper = textwrap.TextWrapper()
    wrapper.width = 80
    wrapper.initial_indent = ' '
    wrapper.subsequent_indent = ' '
    return wrapper.fill(description)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        build(sys.argv[1])
    build()
