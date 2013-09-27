#!/usr/bin/env python

import setuptools
from rdoupdate.core import VERSION


setuptools.setup(
    name='rdoupdate',
    version=VERSION,
    description='module for parsing and creating YAML update files',
    author='Jakub Ruzicka',
    author_email='jruzicka@redhat.com',
    url='https://github.com/yac/rdoupdate',
    packages=['rdoupdate'],
    entry_points={
        "console_scripts": ["rdoupdate-check = rdoupdate.check:main"]
    }
)
