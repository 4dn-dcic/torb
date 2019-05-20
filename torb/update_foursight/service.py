# -*- coding: utf-8 -*-
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


@powerup('update_foursight')
def handler(event, context):
    """
    Use a PUT request to create a Foursight environment for the given
    ElasticBeanstalk environment name and update the event JSON with the
    resulting environment name on success. Also attempt to log to Foursight
    using with a PUT request to checks endpoint.

    `dest_env` in the event JSON determines the ElasticBeanstalk environment.

    Sets the "event" key of the event JSON to the name of created FS environment.
    """
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if dry_run:
        return event
    try:
        foursight = bs.create_foursight_auto(dest_env)
    except Exception as exc:
        logger.warning('Error in update_foursight on bs.create_foursight_auto: %s' % exc)
    else:
        event['foursight'] = foursight
    try:
        # if staging, update the staging build check
        if foursight.get('fs_url') == 'staging':
            check_fields = {'status': 'PASS', 'full_output': 'Updating foursight'}
            bs.log_to_foursight(event, 'update_foursight', check_fields)
    except Exception as exc:
        logger.warning('Error in update_foursight on bs.log_to_foursight: %s' % exc)

    return event
