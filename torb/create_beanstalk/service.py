# -*- coding: utf-8 -*-
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup, get_default
from six import string_types


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def process_overrides(event):
    '''
    Update fields in the event JSON based off of the _override subobject in the
    event. Requires a 'type' in the _override object, which is then looked up
    in the lookups dict.

    _overrides is set from the step function. See "ResultPath":"$._overrides"
    in the workflow definition.
    '''
    # in form: <override type to find>: [<override value>, <field to update>]
    # given: "_override": [{"type": "create_es", "waitfor_details": <val>}],
    # then will set "es_url" = <val> in event JSON
    lookups = {
        'create_rds': ['waitfor_details', 'db_endpoint'],
        'create_es': ['waitfor_details', 'es_url'],
    }

    overrides = event.get('_overrides')

    if overrides and not isinstance(overrides, string_types):
        for override in overrides:
            if override and hasattr(override, 'get'):
                lookup = lookups.get(override.get('type'))
                if lookup and override.get(lookup[0]):
                    event[lookup[1]] = override[lookup[0]]
    return event


@powerup('create_beanstalk')
def handler(event, context):
    """
    Create a new ElasticBeanstalk environment or update it if it already exists.
    Takes a bunch of options from the input JSON and pass them onto
    beanstalk_utils.create_bs, which sets environment variables for the EB env
    and determines what configuration template to use. Check out the docs on
    that function for more specifics.

    Also creates a new Foursight environment with PUT to /api/environments.
    The PUT body contains Fourfront and Elasticsearch urls.

    Adds `prev_bs_version` to the output event, which is the pre-existing
    application version of the ElasticBeanstalk environment, if applicable.
    """
    logger.info("Before processing overrides: %s" % event)
    event = process_overrides(event)
    logger.info("After processing overrides: %s" % event)

    source_env = get_default(event, 'source_env')
    dest_env = get_default(event, 'dest_env')
    db_endpoint = get_default(event, 'db_endpoint')
    es_url = get_default(event, 'es_url')
    dry_run = get_default(event, 'dry_run')
    load_prod = get_default(event, 'load_prod')
    large_instance_beanstalk = get_default(event, 'large_bs')
    fs_url = dest_env

    # overwrite db_endpoint potentially if working with staging/data
    # specifically, if using the ff_deploy_staging workflow, this code is hit
    if 'webprod' in source_env and 'webprod' in dest_env:
        if not db_endpoint:
            db_endpoint = bs.GOLDEN_DB
        # determine fs_url
        fs_url = 'staging'
        if dest_env == bs.whodaman():
            fs_url = 'data'

    retval = {
        "type": "create_bs",
        "id": dest_env,
        "dry_run": dry_run,
        "source_env": source_env,
        "dest_env": dest_env,
    }

    if not dry_run:
        # Make sure we have the required s3 buckets
        try:
            bs.create_s3_buckets(dest_env)
        except Exception as exc:
            logger.info('Error on create_s3_buckets: %s' % exc)
            pass

        # add the previous beanstalk version to event, which is used in the
        # waitfor function down the line
        try:
            prev_bs_info = bs.beanstalk_info(dest_env)
        except Exception as exc:
            logger.warning('create_beanstalk: could not add prev_bs_version to event. %s' % exc)
        else:
            retval['prev_bs_version'] = prev_bs_info['VersionLabel']

        # Create or update ElasticBeanstalk environment
        res = bs.create_bs(dest_env, load_prod, db_endpoint, es_url, large_instance_beanstalk)

        bs_url = res.get('CNAME')
        logger.info("got bs_url as %s" % bs_url)

        # we won't always have bs_url
        if bs_url:
            retval['cname'] = bs_url
            fs_res = bs.create_foursight(dest_env, bs_url, es_url, fs_url)
            logger.info("Created foursightenv with result: %s " % fs_res)
        else:
            logger.info("No beanstalk endpoint yet, can't create foursight env")

        logger.info(res)
    return retval
