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

    retval = {"type": "create_rds",
              "id": item_id,
              "dry_run": dry_run
              }

    if item_id == "fourfront-webprod" or item_id.startswith('fourfront-webprod'):
        print("not deleteing production database")
        retval['info'] = 'skipping prod database'
        return retval

    if not dry_run:
        arn = bs.create_db_from_snapshot(item_id)
        if arn == "Deleting":
            raise bs.WaitingForBoto3("Waiting for RDS to delete")

    return retval
