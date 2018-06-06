# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from dcicutils.beanstalk_utils import WaitingForBoto3
from torb.utils import powerup


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


@powerup('waitfor')
def handler(event, context):
    # get data
    item_id = get_default(event, 'id')
    boto3_type = get_default(event, 'type')
    dry_run = get_default(event, 'dry_run')

    checkers = {'snapshot': bs.is_snapshot_ready,
                'create_rds': bs.is_db_ready,
                'create_es': bs.is_es_ready,
                'create_bs': bs.is_beanstalk_ready,
                'indexing': bs.is_indexing_finished,
                'travis': bs.is_travis_finished}

    if dry_run:
        try:
            logger.warn("Dry Run - would have called %s : %s with %s" %
                        (checkers[boto3_type], boto3_type, item_id))
        except:
            logger.warn("Dry Run, but boto3_type not in checkers")
        status = True
        details = "dry_run"
    else:
        if boto3_type == 'indexing':
            if event.get('bs_version'):
                status, details = checkers[boto3_type](item_id, event.get('bs_version'))
            elif event.get('beanstalk', {}).get('bs_version'):
                status, details = checkers[boto3_type](item_id, event['bs_version']['bs_version'])
            else:
                status, details = checkers[boto3_type](item_id)
        else:
            status, details = checkers[boto3_type](item_id)

    if not status:
        raise WaitingForBoto3("not ready yet, status: %s, details: %s"
                              % (str(status), str(details)))

    # add version if we are waiting for beanstalk being ready
    # with ff_staging_deploy workflow this will actually add to event['beanstalk']['bs_version']
    if boto3_type == 'create_bs' and 'bs_version' not in event and not dry_run:
        info = bs.beanstalk_info(item_id)
        event['bs_version'] = info['VersionLabel']

    event['waitfor_details'] = details
    return event
