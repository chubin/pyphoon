#!/usr/bin/env python
''' Module for setting up pyphoon as a CLI tool
'''
#pylint: disable=unused-import
from setuptools import setup, find_packages

setup(
    name='pyphoon',
    url='https://github.com/chubin/pyphoon',
    author='Igor Chubin',
    author_email='igor@chub.in',
    version='0.2',
    entry_points={
        'console_scripts': [
            'pyphoon=pyphoon:main'
        ],
    },
    scripts=['pyphoon/bin/pyphoon-lolcat'],
    packages=find_packages(),
    install_requires=[
        'python-dateutil'
    ]
)
