# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key, default=None):
    return data.get(key, os.environ.get(key, default))


@powerup('update_foursight')
def handler(event, context):
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if dry_run:
        return event

    foursight = bs.create_foursight_auto(dest_env)

    event['foursight'] = foursight
    try:
        if foursight.get('fs_url') == 'staging':
            # if staging, side effect and update staging_build
            bs.log_to_foursight(event, '', status="PASS",
                                full_output="Updating foursight")
    except AttributeError:
        pass

    return event
