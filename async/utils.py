"""
    Various Python utilities.
"""
from inspect import getmodule


def full_name(function):
    """Return the full name of a function instance.
    """
    if isinstance(function, basestring):
        return function
    module_name = getmodule(function).__name__
    return '.'.join([module_name, function.func_name])

