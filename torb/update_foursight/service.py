# -*- coding: utf-8 -*-
import os
import logging
import torb.beanstalk_utils as bs
from torb.utils import powerup


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key, default=None):
    return data.get(key, os.environ.get(key, default))


@powerup('update_foursight')
def handler(event, context):
    dest_env = get_default(event, 'dest_env')
    # src_env = get_default(event, 'src_env')
    # is_data = get_deafult(event, 'is_src_data')
    dry_run = get_default(event, 'dry_run')

    if not dry_run:
        # create env
        info = bs.beanstlk_config(dest_env)
        logger.INFO(info)
        # es_url = get_env_var(info, 'ES_URL')
    return event
