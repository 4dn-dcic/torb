# -*- coding: utf-8 -*-
import logging
from dcicutils import beanstalk_utils as bs
from dcicutils.beanstalk_utils import WaitingForBoto3
from ..utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


@powerup('waitfor')
def handler(event, context):
    """
    Utility lambda meant to be the glue in workflows. Takes a `type` in the
    event JSON that is used to look up a "checker" function in the checkers
    dict; these should have a standarized output. Also takes a generic `item_id`
    from the event, which is passed to the checker function.

    Use along with a "Retry" block when defining a workflow to wait until the
    condition specified by the checker function is met. Below is an example,
    which will retry when `WaitingForBoto3` Exception is encountered:
    "Retry":[
      {
        "ErrorEquals":[
          "WaitingForBoto3"
        ],
        "IntervalSeconds":30,
        "MaxAttempts":100,
        "BackoffRate":1.0
      }
    ],

    Updates the `waitfor_details` for the event, which may be overwritten
    if you don't handle with a specific "ResultPath" definition in the workflow
    """
    item_id = get_default(event, 'id')
    boto3_type = get_default(event, 'type')
    dry_run = get_default(event, 'dry_run')

    # these are checker functions that correspond to beanstalk_utils fxns
    # the keys correspond to the 'type' that was last overwritten in event JSON
    checkers = {'snapshot': bs.is_snapshot_ready,
                'create_rds': bs.is_db_ready,
                'create_es': bs.is_es_ready,
                'create_bs': bs.is_beanstalk_ready,
                'indexing': bs.is_indexing_finished,
                'travis_start': bs.is_travis_started,
                'travis_finish': bs.is_travis_finished}

    if dry_run:
        try:
            logger.warning("Dry Run - would have called %s : %s with %s"
                           % (checkers[boto3_type], boto3_type, item_id))
        except Exception:
            logger.warning("Dry Run, but boto3_type not in checkers")
        status = True
        event["waitfor_details"] = "dry_run"
        return event

    if boto3_type not in checkers:
        raise Exception('waitfor error: boto3_type %s not in checkers' % boto3_type)
    checker_fxn = checkers[boto3_type]

    # define custom checker fxn input
    if boto3_type == 'indexing':
        # if we have a previous bs version and travis build id, pass them
        # to the is_indexing_finished check function
        prev_bs_version = event.get('beanstalk', {}).get('prev_bs_version')
        travis_build_id = event.get('travis', {}).get('build_id')
        status, details = checker_fxn(item_id, prev_version=prev_bs_version,
                                      travis_build_id=travis_build_id)
    else:
        status, details = checker_fxn(item_id)

    if not status:
        raise WaitingForBoto3("not ready yet, status: %s, details: %s"
                              % (status, details))

    # define custom checker fxn output
    if boto3_type == 'travis_start':
        if 'travis' in event:
            event['travis']['build_id'] = details['builds'][0]['id']

    event['waitfor_details'] = details
    return event
