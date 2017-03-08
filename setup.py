import os
from setuptools import setup
import sys

def read(fname1, fname2):
    if os.path.exists(fname1):
        fname = fname1
    else:
        fname = fname2
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "django-async",
    version = "0.7.2",
    author = "Kirit Saelensminde",
    author_email = "kirit@felspar.com",
    url='http://www.kirit.com/Django%20Async',
    description = "Asynchronous task execution with proper database transaction management for Django",
    long_description = read('README','README.markdown'),
    license = "Boost Software License - Version 1.0 - August 17th, 2003",
    keywords = "django async taskqueue task queue",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved",
    ],
    install_requires = ['lockfile', 'simplejson'],
    packages = ['async',
        'async.tests',
        'async.management',
        'async.management.commands',
        'async.migrations',
        'async.south_migrations',
    ]
)
