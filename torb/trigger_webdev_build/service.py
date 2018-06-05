# -*- coding: utf-8 -*-
import os
import logging
from torb.utils import kick_travis_build


logger = logging.getLogger()
logger.setLevel(logging.INFO)
travis_key = os.environ.get('travis_key')


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


def handler(event, context):
    # get data
    branch = get_default(event, 'branch')
    repo_owner = get_default(event, 'repo_owner')
    repo_name = get_default(event, 'repo_name')

    kick_travis_build(branch, repo_owner, repo_name, 'fourfront-webdev', travis_key)
    return {"Status": "OK"}
