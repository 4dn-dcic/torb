# -*- coding: utf-8 -*-
import os
import logging
import torb.beanstalk_utils as bs
from torb.utils import powerup
from six import string_types


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


def process_overrides(event):
    '''tries to find the values we need in _overrides
    assume _overrides to be list of objects
    '''
    # lookups is dict mapping override type to the field that stores
    # the information we want, to the name the field should be in events
    lookups = {'create_rds': ['waitfor_details', 'db_endpoint'],
               'create_es': ['waitfor_details', 'es_url'],
               }

    rides = event.get('_overrides')

    if rides and not isinstance(rides, string_types):
        for item in rides:
            if item and hasattr(item, 'get'):
                lookup = lookups.get(item.get('type'))
                if lookup:
                    event[lookup[1]] = item.get(lookup[0])
    return event


@powerup('create_beanstalk')
def handler(event, context):
    event = process_overrides(event)
    logger.info("after processing")
    logger.info(event)

    source_env = get_default(event, 'source_env')
    dest_env = get_default(event, 'dest_env')
    db_endpoint = get_default(event, 'db_endpoint')
    es_url = get_default(event, 'es_url')
    dry_run = get_default(event, 'dry_run')
    load_prod = get_default(event, 'load_prod')
    large_instance_beanstalk = get_default(event, 'large_bs')

    # overwrite db_endpoint potentially
    if ('webprod' in source_env and 'webprod' in dest_env and not db_endpoint):
        db_endpoint = bs.GOLDEN_DB

    retval = {"type": "create_bs",
              "id": dest_env,
              "dry_run": dry_run,
              "source_env": source_env,
              "dest_env": dest_env,
              }

    if not dry_run:
        # make sure we have appropriate s3_buckets
        try:
            bs.create_s3_buckets(dest_env)
        except:
            pass
        # create env
        res = bs.create_bs(dest_env, load_prod, db_endpoint, es_url, large_instance_beanstalk)

        bs_url = res.get('CNAME')
        logger.info("got bs_url as %s" % bs_url)

        # we won't always have bs_url
        if bs_url:
            retval['cname'] = bs_url
            fs_res = bs.create_foursight(dest_env, bs_url, es_url)
            logger.info("create foursight with result = %s " % fs_res)
        else:
            logger.info("No beanstalk endpoint yet, can't create foursight monitoring")

        logger.info(res)
    return retval
