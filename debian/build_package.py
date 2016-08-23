#!/usr/bin/env python3

from subprocess import check_call
import os


def build():
    os.environ['DEBFULLNAME'] = 'Nathaniel Schaaf'
    os.environ['DEBEMAIL'] = 'nschaaf@wikimedia.org'

    check_call(['debchange',
                '--create',
                '--package',
                'python3-recommendation',
                '--newversion',
                '0.0.1-1',
                '--distribution',
                'unstable',
                '--force-distribution',
                '--preserve',
                'Please contact the maintainer for details about this software.'])

    check_call(['debuild', '--no-tgz-check', '-us', '-uc', '-b'])

if __name__ == '__main__':
    build()
