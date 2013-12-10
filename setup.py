#!/usr/bin/env python

from setuptools import find_packages, setup

from haddock import version


setup(
    name='haddock',
    description='Mini-Framework for making APIs.',
    version=version.base(),
    author='HawkOwl',
    author_email='hawkowl@atleastfornow.net',
    url='https://github.com/hawkowl/haddock',
    packages=find_packages(),
    package_data={
        },
    scripts=[
        ],
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"
        ],
    keywords=[
        "twisted", "klein", "api"
        ],
    install_requires=[
        "klein"
        ],
    long_description=file('README.md').read()
)
