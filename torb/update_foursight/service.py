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
    dry_run = get_default(event, 'dry_run')
    foursight_data = {'dest_env': dest_env,
                      'fs_url': dest_env}

    # whats our url
    foursight_data['bs_url'] = bs.get_beanstalk_real_url(dest_env)
    if 'data.4dnucleome.org' in foursight_data['bs_url']:
        foursight_data['fs_url'] = 'data'
    elif 'staging.4dnucleome.org' in foursight_data['bs_url']:
        foursight_data['fs_url'] = 'staging'
        # if staging, side effect and update staging_build
        bs.log_to_foursight(event, '', status="PASS",
                            full_ouput="Updating foursight")

    if not dry_run:
        foursight_data['es_url'] = bs.get_es_from_health_page(foursight_data['bs_url'])
        event['foursight'] = bs.create_foursight(**foursight_data)
        if event['foursight'].get('initial_checks'):
            del event['foursight']['initial_checks']

    return event
