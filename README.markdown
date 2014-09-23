Django Async is an asynchronous execution queue for Django with proper database transaction management.

Building a database backed task queue is a fairly trivial thing, but getting the database transactions exactly right is no simple matter.

[![Build Status](https://travis-ci.org/KayEss/django-async.png?branch=develop)](https://travis-ci.org/KayEss/django-async)


# Usage and documentation #

All documentation can be found at http://www.kirit.com/Django%20Async

## New in the development branch ##

### Job cancellation ###

There is now a separate `cancelled` field  on jobs which can be used to mark those which are no longer to be run.

### Groups ###

There is now an optional job grouping in `async.models.Group`. Jobs can be placed into a group so that related jobs can be tracked together.

# Doing development #

_This project uses git flow. Don't forget to do `git flow init -d`_

To create virtual environments for running the tests you can execute `test-projects/make-virtual-environments`. To run the tests execute `runtests`.
