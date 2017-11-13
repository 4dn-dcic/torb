# -*- coding: utf-8 -*-
import requests
import os
import logging
import json
from torb.utils import powerup

logger = logging.getLogger()
logger.setLevel(logging.INFO)
travis_key = os.environ.get('travis_key')


def get_default(data, key):
    return data.get(key, os.environ.get(key, None))


@powerup('travis_deploy')
def handler(event, context):
    # setup path to run git
    merge_into = get_default(event, 'merge_into')
    repo_owner = get_default(event, 'repo_owner')
    repo_name = get_default(event, 'repo_name')
    branch = get_default(event, 'branch')
    dest_env = get_default(event, 'dest_env')

    if not dest_env:
        dest_env = 'fourfront-webdev'
    dry_run = get_default(event, 'dry_run')
    print("trigger build for %s/%s on branch %s" % (repo_owner, repo_name, branch))
    if dry_run:
        return

    # overwrite the before_install section (travis doesn't allow append)
    # by adding the tibanna-deploy env variable, which will trigger the deploy
    body = {
            "request": {
                "message": "Your Tibanna triggered build has started.  Have a nice day! :)",
                "branch": branch,
                "config": {
                    "before_install": ["export tibanna_deploy=%s" % (dest_env),
                                       "echo $tibanna_deploy",
                                       "postgres --version",
                                       "initdb --version",
                                       "nvm install 4",
                                       "node --version",
                                       "npm config set python /usr/bin/python2.7"
                                       ]
                    }
                }
            }

    # if merge into, merge branch into merge_into branch and deploy merge_into branch
    if merge_into:
        logger.info("setting env for tibanna_merge to %s" % merge_into)
        body['request']['config']['before_install'].append('export tibanna_merge=%s' % (merge_into))
        body['request']['config']['before_install'].append('echo $tibanna_merge')

    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Travis-API-Version': '3',
               'User-Agent': 'tibanna/0.1.0',
               'Authorization': 'token %s' % travis_key
               }

    url = 'https://api.travis-ci.org/repo/%s%s%s/requests' % (repo_owner, '%2F', repo_name)

    resp = requests.post(url, headers=headers, data=json.dumps(body))

    try:
        logger.info(resp)
        logger.info(resp.text)
        logger.info(resp.json())
    except:
        pass

    return resp.text
