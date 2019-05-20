# -*- coding: utf-8 -*-
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


@powerup('update_bs_config')
def handler(event, context):
    """
    Update the configuration template for an existing ElasticBeanstalk env.
    Pass in the EB environment name in the event JSON as `dest_env` and the
    configuration template at `template`. If no template is specified, will
    use "fourfront-base" by default

    Updates `waitfor_details` in the event JSON after the update
    """
    template = get_default(event, 'update-template', 'fourfront-base')
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if not dry_run:
        # update environment, keeping current EB env variables
        res = bs.update_bs_config(dest_env, template, True)
        logger.info(res)
        event['waitfor_details'] = 'http://' + res['CNAME']
        event['type'] = 'create_bs'
    return event
