"""
    Various Python utilities.
"""
from inspect import getmembers, getmodule, isfunction, ismethod


def full_name(item):
    """Return the full name of a something passed in so it can be retrieved
    later on.
    """
    if isinstance(item, basestring):
        return item
    if ismethod(item):
        module_name = full_name(dict(getmembers(item))['im_self'])
    else:
        module_name = getmodule(item).__name__
    if isfunction(item):
        name = item.func_name
    else:
        name = item.__name__
    return '.'.join([module_name, name])


def object_at_end_of_path(path):
    """Attempt to return the Python object at the end of the dotted
    path by repeated imports and attribute access.
    """
    access_path = path.split('.')
    for index in xrange(1, len(access_path)-1):
        try:
            # import top level module
            module_name = '.'.join(access_path[:-index])
            module = __import__(module_name)
        except ImportError:
            continue
        else:
            for step in access_path[1:-1]: # walk down it
                module = getattr(module, step)
            break
    return getattr(module, access_path[-1])


def non_unicode_kwarg_keys(kwargs):
    """Convert all the keys to strings as Python won't accept unicode.
    """
    return dict([(str(k), v) for k, v in kwargs.items()]) if kwargs else {}
