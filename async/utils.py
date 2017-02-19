"""
    Various Python utilities.
"""
from inspect import getmembers, getmodule, ismethod

try:
    _ = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    # pylint: disable=redefined-builtin,invalid-name
    unicode = str
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    pass

def full_name(item):
    """Return the full name of a something passed in so it can be retrieved
    later on.
    """

    if isinstance(item, basestring):
        return item
    if ismethod(item):
        module_name = full_name(dict(getmembers(item))['__self__'])
    else:
        module_name = getmodule(item).__name__
    name = item.__name__
    return '.'.join([module_name, name])


def object_at_end_of_path(path):
    """Attempt to return the Python object at the end of the dotted
    path by repeated imports and attribute access.
    """
    access_path = path.split('.')
    module = None
    for index in range(1, len(access_path)):
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
    if module:
        return getattr(module, access_path[-1])
    else:
        return globals()['__builtins__'][path]


def non_unicode_kwarg_keys(kwargs):
    """Convert all the keys to strings as Python won't accept unicode.
    """
    return dict([(str(k), v) for k, v in kwargs.items()]) if kwargs else {}
