#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_1_7.settings")

    # Add the top level to the path so we can find async_exec
    sys.path.append('../..')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
