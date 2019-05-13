# -*- coding: utf-8 -*-
import requests
import os
import logging
import json
from torb.utils import (
    powerup,
    get_travis_config,
    get_default
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# authentication issues are related to account-based travis authentication
# travis_key is access key: https://docs.travis-ci.com/user/triggering-builds
travis_key = os.environ.get('travis_key')


@powerup('travis_deploy')
def handler(event, context):
    """
    Generic lambda for triggering a travis build that will deploy to any given
    `dest_env` ElasticBeanstalk environment. Builds and deploys using the
    `branch` from the event JSON.
    `merge_into` is an optional Fourfront branch that, if provided, will have
    `branch` merged into it at the end of the successful Travis build.

    Will set `type` and `id` in waitfor, as well as `travis` subobject in
    event to keep track of the generated Travis request ID.

    The code here looks very similar to utils.kick_travis_build, but is
    different as it handles merge_into and checking of the travis response.
    """
    # setup path to run git
    merge_into = get_default(event, 'merge_into')
    repo_owner = get_default(event, 'repo_owner')
    repo_name = get_default(event, 'repo_name')
    branch = get_default(event, 'branch')
    dest_env = get_default(event, 'dest_env')
    dry_run = get_default(event, 'dry_run')

    if not dest_env:
        event['torb_message'] = 'Must specify ElasticBeanstalk dest_env in event'
        return event

    logger.info("trigger build for %s/%s on branch %s" % (repo_owner, repo_name, branch))
    if dry_run:
        return event

    # overwrite the before_install section (travis doesn't allow append)
    # by adding the tibanna-deploy env variable, which will trigger the deploy
    # TODO: add in snovault check to before_install
    body = {
        "request": {
            "message": "travis-deploy: Torb triggered build to %s has started" % dest_env,
            "branch": branch,
            "config": {
                "before_install": ["export tibanna_deploy=%s" % (dest_env)] +
                get_travis_config(branch, repo_name, repo_owner).get('before_install', [])
            }
        }
    }

    # if merge into, merge branch into merge_into branch and deploy merge_into branch
    # this is done using 'tibanna_merge' env var and deploy/deploy_beanstalk.py in Fourfront
    if merge_into:
        logger.info("setting env for tibanna_merge to %s" % merge_into)
        body['request']['config']['before_install'].append('export tibanna_merge=%s' % (merge_into))
        body['request']['config']['before_install'].append('echo $tibanna_merge')

    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Travis-API-Version': '3',
               'User-Agent': 'tibanna/0.1.0',
               'Authorization': 'token %s' % travis_key}

    url = 'https://api.travis-ci.org/repo/%s%s%s/requests' % (repo_owner, '%2F', repo_name)

    resp = requests.post(url, headers=headers, data=json.dumps(body))
    if resp.ok:
        logger.info("Successfully triggered Travis build. Info: %s" % resp.json())
        # get request id and use it to find build id
        req_id = resp.json()['request']['id']
        req_url = ('https://api.travis-ci.org/repo/%s%s%s/request/%s'
                  % (repo_owner, '%2F', repo_name, req_id)
        # set id and type for waitfor
        event['type'] = 'travis_start'
        event['id'] = req_url
        event['travis'] = {'request_id': req_id, 'request_url': req_url}
        return event
    else:
        logger.info('Could not trigger Travis build. Info: %s' % resp.text)
        raise Exception(resp.text)
