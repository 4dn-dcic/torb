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


def get_es(env):
    info = bs.beanstalk_config(env)
    return [setting['Value'] for setting in
            info['ConfigurationSettings'][0]['OptionSettings']
            if setting['OptionName'] == 'ES_URL'][0]


@powerup('set_bs_env')
def handler(event, context):
    env_vars = get_default(event, 'env_vars')
    template = get_default(event, 'template')
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if 'ENV_NAME' not in env_vars.keys():
        env_vars['ENV_NAME'] = dest_env
    if 'ES_URL' not in env_vars.keys():
        env_vars['ES_URL'] = get_es(dest_env)

    if not dry_run:
        # create env
        res = bs.set_bs_env(dest_env, env_vars, template)
        logger.info(res)
        event['id'] = dest_env
        event['waitfor_details'] = 'http://' + res['CNAME']
        event['type'] = 'create_bs'
        del event['template']
    return event
