# -*- coding: utf-8 -*-
import requests
import os
import logging
import json
from dcicutils import beanstalk_utils as bs


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
    print("trigger build for %s/%s on branch %s" % (repo_owner, repo_name, branch))

    # we need to start the cloneing / building of a new staging environment so it will
    # hopefully be ready to deploy to by the time the travis build finishes,
    # as last step in travis build will attempt to deploy to this new environemnt
    env = "fourfront-staging"
    import time

    global_start = time.time()
    start = time.time()
    bs.add_es(env)
    end = time.time()
    print("Start creation of ES took %s " % str(end - start))

    start = time.time()
    db_endpoint = bs.snapshot_db('fourfront-webprod', env)
    end = time.time()
    print("Start creation of DB took %s " % str(end - start))

    start = time.time()
    es_endpoint = bs.get_es_build_status(env)
    end = time.time()
    print("Wait for ES took %s " % str(end - start))

    start = time.time()
    bs.clone_bs_env('fourfront-webprod', env, True, db_endpoint, es_endpoint)

    end = time.time()
    print("Start clone env took %s " % str(end - start))

    # overwrite the before_install section (travis doesn't allow append)
    # by adding the tibanna-deploy env variable, which will trigger the deploy
    body = {
            "request": {
                "message": "Tibanna triggered stagging build has started.  Have a nice day! :)",
                "branch": branch,
                "config": {
                    "before_install": ["export tibanna_deploy=fourfront-staging",
                                       "echo $tibanna_deploy",
                                       "postgres --version",
                                       "initdb --version",
                                       "nvm install 8",
                                       "node --version",
                                       "npm config set python /usr/bin/python2.7",
                                       "curl -O  ${ES_DOWNLOAD_URL} && sudo dpkg -i --force-confnew elasticsearch-${ES_VERSION}.deb",
                                       "sudo service elasticsearch stop"
                                       ]
                    }
                }
            }

    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Travis-API-Version': '3',
               'User-Agent': 'tibanna/0.1.0',
               'Authorization': 'token %s' % travis_key
               }

    url = 'https://api.travis-ci.org/repo/%s%s%s/requests' % (repo_owner, '%2F', repo_name)

    resp = requests.post(url, headers=headers, data=json.dumps(body))

    globalend = time.time()
    print("Whole Enchilada took %s " % str(globalend - global_start))

    try:
        logger.info(resp)
        logger.info(resp.text)
        logger.info(resp.json())
    except:
        pass
