# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


@powerup('snapshot_rds')
def handler(event, context):
    """
    Run beanstalk_utils.create_db_snapshot, which will snapshot the RDS instance
    with `db_id` and use `snapshot_id` as the snapshot identifier. If a current
    snapshot already exists with this id, it will delete it.
    """
    # get data
    db_id = get_default(event, 'db_id')
    snapshot_id = get_default(event, 'snapshot_id')
    dry_run = get_default(event, 'dry_run')

    if dry_run:
        res = "Dry Run - would have ran create_db_snapshot(%s, %s)" % (db_id, snapshot_id)
        ret_dbid = "dry_run"
    else:
        res = bs.create_db_snapshot(db_id, snapshot_id)
        if res == "Deleting":
                raise bs.WaitingForBoto3("Waiting for RDS to delete")

        ret_dbid = res['DBSnapshot']['DBSnapshotIdentifier']
    logger.info(res)

    return {'type': 'snapshot', 'id': ret_dbid, 'dry_run': dry_run}
