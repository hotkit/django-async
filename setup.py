import os
from setuptools import setup

def read(fname1, fname2):
    if os.path.exists(fname1):
        fname = fname1
    else:
        fname = fname2
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-async",
    version = "0.2.2.9",
    author_email = "kirit@felspar.com",
    description = ("Asynchronous task execution for Django"),
    long_description = read('README','README.markdown'),
    license = "Boost Software License - Version 1.0 - August 17th, 2003",
    keywords = "django async taskqueue task queue",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Boost Software License - Version 1.0 - August 17th, 2003",
    ],
    install_requires = ['simplejson'],
    packages = ['async',
        'async.tests',
        'async.management',
        'async.management.commands'],
)
