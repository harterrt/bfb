#!/usr/bin/env python
from setuptools import setup, find_packages

test_deps = [
    'coverage',
    'pytest-cov',
    'pytest',
]

extras = {
    'testing': test_deps,
}

setup(
    name='bfb',
    version='0.1',
    description='ETL for Black Forest Brewery',
    author='Ryan Harter',
    author_email='harterrt@gmail.com',
    url='https://github.com/harterrt/bfb',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
    ],
    tests_require=test_deps,
    extras_require=extras,
)
