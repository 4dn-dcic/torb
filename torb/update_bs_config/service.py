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


@powerup('update_bs_config')
def handler(event, context):
    template = get_default(event, 'update-template', 'fourfront-base')
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if not dry_run:
        # create env
        res = bs.update_bs_config(dest_env, template, True)
        logger.info(res)
        event['id'] = 'http://' + res['CNAME']
        event['waitfor_details'] = 'http://' + res['CNAME']
        event['type'] = 'create_bs'
    return event
