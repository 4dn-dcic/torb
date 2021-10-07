# -*- coding: utf-8 -*-
import logging
from dcicutils import beanstalk_utils as bs
from dcicutils.env_utils import is_stg_or_prd_env
from ..utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


@powerup('create_rds')
def handler(event, context):
    """
    Run beanstalk_utils.create_db_from_snapshot, which will create a DB
    from a given snapshot. The `dest_env` from event is used as the DB instance
    name, and if a current db already exists with this name, it will attempt to
    delete it first. For this reason, do NOT proceed when `dest_env` is a production env.

    The `snapshot_arn` from the event is the ARN of the RDS snapshot to restore.
    """
    # get data
    item_id = get_default(event, 'dest_env')
    snapshot_arn = get_default(event, 'snapshot_arn')
    dry_run = get_default(event, 'dry_run')

    retval = {"type": "create_rds", "id": item_id, "dry_run": dry_run}

    if is_stg_or_prd_env(item_id):
        logger.info("Not deleting production DB! Given instance: %s" % item_id)
        retval['torb_message'] = 'create_rds: skipping instance %s' % item_id
        return retval

    if not dry_run and (item_id and snapshot_arn):
        arn = bs.create_db_from_snapshot(item_id, snapshot_arn)
        if arn == "Deleting":
            raise bs.WaitingForBoto3("Waiting for RDS to delete")

    return retval
