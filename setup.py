import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_async",
    version = "0.2",
    author_email = "kirit@felspar.com",
    description = ("Asynchronous task execution for Django"),
    long_description = read('README.markdown'),
    license = "Boost Software License - Version 1.0 - August 17th, 2003",
    keywords = "django async taskqueue task queue",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Boost Software License - Version 1.0 - August 17th, 2003",
    ],
    packages = ['async_exec'],
    install_requires = ['roles'],
    dependency_links = [
        'git://github.com/amolenaar/roles.git'],
)
