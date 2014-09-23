#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_1_4.settings")
# Add the top level to the path so we can find async_exec
sys.path.append('../..')

from async.api import schedule
from async.models import Group


def fast_job(*args):
    pass

def make_group(number):
    group = Group.objects.create(reference=unicode(number))
    outof = number * 100
    for index in range(1, outof):
        schedule(fast_job, args=[number, index, outof], group=group)
    last = schedule(make_group, args=[number+1])
    group.on_completion(last)


if __name__ == "__main__":
    schedule('speed.make_group', args=[1])

