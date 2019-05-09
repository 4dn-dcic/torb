# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


@powerup('create_es')
def handler(event, context):
    """
    Ensure an Elasticsearch instance is create with name given by `dest_env`.
    If force_new, will make a new ES instance, possibly with new
    identifier if `dest_env` is already used. Otherwise, only create a
    new ES if one named `dest_env does not exist`
    """
    # get data
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')
    force_new = get_default(event, 'force_new_es')

    if not dry_run:
        bs.add_es(dest_env, force_new)

    return {"type": "create_es", "id": dest_env, "dry_run": dry_run}
