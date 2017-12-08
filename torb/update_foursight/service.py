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

    if 'webprod' in dest_env:
        urls = {'staging': 'http://staging.4dnucleome.org',
                'data': 'https://data.4dnucleome.org'}
        data_env = bs.whodaman()

        if data_env == dest_env:
            foursight_data['bs_url'] = urls['data']
            foursight_data['fs_url'] = 'data'
        else:
            foursight_data['bs_url'] = urls['staging']
            foursight_data['fs_url'] = 'staging'
            # if staging, side effect and update staging_build
            bs.log_to_foursight(event, '', status="PASS",
                                full_ouput="Updating foursight")

    else:  # get bs url from beanstalk
        bs_info = bs.beanstalk_info(dest_env)
        foursight_data['bs_url'] = bs_info['CNAME']

    if not dry_run:
        foursight_data['es_url'] = bs.get_es_from_health_page(foursight_data['bs_url'])
        event['foursight'] = bs.create_foursight(**foursight_data)
        if event['foursight'].get('initial_checks'):
            del event['foursight']['initial_checks']

    return event
