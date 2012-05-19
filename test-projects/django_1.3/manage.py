#!/usr/bin/env python
from django.core.management import execute_manager
import imp
import sys
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

# Add the top level folder where async_exec is to the paths.
# This is only required for development. Do not do this when you pip install the files.
sys.path.append('../..')

import settings

if __name__ == "__main__":
    execute_manager(settings)
