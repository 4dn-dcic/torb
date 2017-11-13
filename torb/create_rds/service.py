# -*- coding: utf-8 -*-
import os
import logging
import torb.beanstalk_utils as bs


logging.basicConfig()
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


def handler(event, context):
    # get data
    item_id = get_default(event, 'id')
    dry_run = get_default(event, 'dry_run')

    if not dry_run:
        arn = bs.create_db_from_snapshot(item_id)
        if arn == "Deleting":
            raise bs.WaitingForBoto3("Waiting for RDS to delete")

    retval = {"type": "create_rds",
              "id": item_id,
              "dry_run": dry_run
              }
    return retval
