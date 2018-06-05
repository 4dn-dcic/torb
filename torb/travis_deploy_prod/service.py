# -*- coding: utf-8 -*-
import os
from torb.utils import kick_travis_build


travis_key = os.environ.get('travis_key')


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


def handler(event, context):
    # get data
    branch = get_default(event, 'branch')
    repo_owner = get_default(event, 'repo_owner')
    repo_name = get_default(event, 'repo_name')

    kick_travis_build(branch, repo_owner, repo_name, 'fourfront-webprod', travis_key)
    return {"Status": "OK"}
