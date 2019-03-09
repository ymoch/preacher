#!/usr/bin/env python

"""Setting up script for Preacher."""

import os

import setuptools

from preacher import (
    __version__ as VERSION,
    __author__ as AUTHOR,
    __author_email__ as AUTHOR_EMAIL,
    NAME,
    DESCRIPTION,
    URL,
    LICENSE,
)


def load_long_description():
    """Load the long description."""
    readme_file_path = os.path.join(os.path.dirname(__file__), 'README.rst')
    with open(readme_file_path) as readme_file:
        return readme_file.read()


setuptools.setup(
    name=NAME,
    description=DESCRIPTION,
    long_description=load_long_description(),
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'preacher=preacher.app.cli:main'
        ]
    },
    install_requires=[
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pytest-pep8',
        'pytest-flakes',
        'pytest-mypy',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing :: Acceptance',
    ]
)
