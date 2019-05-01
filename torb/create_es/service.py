# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


@powerup('create_es')
def handler(event, context):
    # get data
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')
    force_new = get_default(event, 'force_new_es')

    if not dry_run:
        # if force_new, will make a new ES instance, possibly with new
        # identifier if `dest_env` is already used. Otherwise, only create a
        # new ES if one named `dest_env does not exist`
        bs.add_es(dest_env, force_new)

    return {"type": "create_es", "id": dest_env, "dry_run": dry_run}
