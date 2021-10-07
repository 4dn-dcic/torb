# -*- coding: utf-8 -*-
import os
import logging
from ..utils import kick_travis_build, get_default


logger = logging.getLogger()
logger.setLevel(logging.INFO)
travis_key = os.environ.get('travis_key')


def handler(event, context):
    """
    Use kick_travis_build to request travis.yml from the correct location and
    kick off a travis build with `tibanna_deploy=fourfront-webdev` in the env,
    causing a deployment to the that ElasticBeanstalk environment.
    """
    # get data
    branch = get_default(event, 'branch')
    repo_owner = get_default(event, 'repo_owner')
    repo_name = get_default(event, 'repo_name')

    kick_travis_build(branch, repo_owner, repo_name, 'fourfront-webdev', travis_key)
    return {"Status": "OK", "event": event}
