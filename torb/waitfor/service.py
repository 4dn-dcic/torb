# -*- coding: utf-8 -*-
import os
import logging
import torb.beanstalk_utils as bs
from torb.beanstalk_utils import WaitingForBoto3
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
        status, details = checkers[boto3_type](item_id)
    if not status:
        raise WaitingForBoto3("not ready yet, status: %s, details: %s"
                              % (str(status), str(details)))

    event['waitfor_details'] = details
    event['id'] = details
    return event
