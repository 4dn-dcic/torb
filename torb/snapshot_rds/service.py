# -*- coding: utf-8 -*-
import os
import logging
from dcicutils import beanstalk_utils as bs
from torb.utils import powerup


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


@powerup('snapshot_rds')
def handler(event, context):
    # get data
    source = get_default(event, 'source_env')
    dest = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if dry_run:
        res = "Dry Run - would have ran create_db_snapshot(%s, %s)" % (source, dest)
        dbid = "dry_run"
    else:
        res = bs.create_db_snapshot(source, dest)
        if res == "Deleting":
                raise bs.WaitingForBoto3("Waiting for RDS to delete")

        dbid = res['DBSnapshot']['DBSnapshotIdentifier']
    logger.info(res)

    return {'type': 'snapshot',
            'id': dbid,
            'dry_run': dry_run,
            }
