#!/usr/bin/env python

import setuptools
from rdoupdate import VERSION


setuptools.setup(
    name='rdoupdate',
    version=VERSION,
    description='managing special packaging/update repository',
    author='Jakub Ruzicka',
    author_email='jruzicka@redhat.com',
    url='https://github.com/yac/rdoupdate',
    packages=['rdoupdate', 'rdoupdate.utils'],
    entry_points={
        "console_scripts": ["rdoupdate = rdoupdate.shell:main"]
    }
)
