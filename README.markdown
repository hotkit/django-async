Django Async is an asynchronous execution queue for Django with proper database transaction management.

Building a database backed task queue is a fairly trivial thing, but getting the database transactions exactly right is no simple matter.

[![Build Status](https://travis-ci.org/KayEss/django-async.png?branch=develop)](https://travis-ci.org/KayEss/django-async)


# Usage and documentation #

All documentation can be found at http://www.kirit.com/Django%20Async

# Doing development #

_This project uses git flow. Don't forget to do `git flow init -d`_

To test just run `tox`. But if you want to go the old way then to create virtual environments for running the tests you can execute `test-projects/make-virtual-environments`. To run the tests execute `runtests`.
