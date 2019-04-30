# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup, get_default


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


@powerup('create_rds')
def handler(event, context):
    """
    Run beanstalk_utils.create_db_from_snapshot, which will create a DB
    from a given snapshot. The `db_id` from the event is used as the DB instance
    name, and if a current db already exists with this name, it will attempt to
    delete it first. For this reason, do NOT proceed when `db_id` is
    fourfront-webprod or fourfront-webprod2.

    The `snapshot_arn` from the event is the ARN of the RDS snapshot to restore.
    """
    # get data
    item_id = get_default(event, 'db_id')
    snapshot_arn = get_default(event, 'snapshot_arn')
    dry_run = get_default(event, 'dry_run')

    retval = {"type": "create_rds", "id": item_id, "dry_run": dry_run}

    if 'fourfront-webprod' in id:
        print("not deleting production database")
        retval['info'] = 'skipping prod database'
        return retval

    if not dry_run and (item_id and snapshot_arn):
        arn = bs.create_db_from_snapshot(item_id, snapshot_arn)
        if arn == "Deleting":
            raise bs.WaitingForBoto3("Waiting for RDS to delete")

    return retval
