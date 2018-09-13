#!/usr/bin/env python

import os.path
from setuptools import setup

readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
requirements_file = os.path.join(os.path.dirname(__file__),
                                 'requirements.txt')

with open(requirements_file, 'rt') as f:
    requirements = f.readlines()

setup(
    name='yamodool',
    version='0.0.1',
    description='YAML Models for Odoo',
    author='Center of Research & Development',
    # author_email='info@crnd.pro',
    url='https://crnd.pro',
    long_description=open(readme_file).read(),
    packages=[
        'yamodool',
    ],
    license="MPL 2.0",
    classifiers=[
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=[
        'odoo', 'yaml'
    ],
    install_requires=requirements,
)
