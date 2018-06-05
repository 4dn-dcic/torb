from __future__ import print_function
import requests
import yaml
import os
import json
import logging
from dcicutils.beanstalk_utils import log_to_foursight

########################################
# These utils exclusively live in Torb #
########################################

###########################
# Config
###########################
LOG = logging.getLogger(__name__)


def get_travis_config(branch='master', repo='fourfront', gh_user='4dn-dcic', filename='.travis.yml'):
    fourfront_travis_yml_url = 'https://raw.githubusercontent.com/{}/{}/{}/{}'.format(gh_user, repo, branch, filename)
    return yaml.load(requests.get(fourfront_travis_yml_url).content)


def kick_travis_build(branch, repo_owner, repo_name, env, travis_key=None):
    print("trigger build for %s/%s on branch %s" % (repo_owner, repo_name, branch))

    if travis_key is None:
        travis_key = os.environ.get('travis_key')

    # overwrite the before_install section (travis doesn't allow append)
    # by adding the tibanna-deploy env variable, which will trigger the deploy
    body = {
        "request": {
            "message": "Torb triggered build to " + env + " has started.  Have a nice day! :)",
            "branch": branch,
            "config": {
                "before_install": ["export tibanna_deploy=" + env] +
                get_travis_config(branch, repo_name, repo_owner).get('before_install', [])
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

    try:
        LOG.info(resp)
        LOG.info(resp.text)
        LOG.info(resp.json())
    except:
        pass

    return resp


def powerup(lambda_name):
    '''
    friendly wrapper for your lambda functions... allows for fun with
    input json amongst other stuff
    '''
    def decorator(function):
        import logging
        logging.basicConfig()
        logger = logging.getLogger('logger')

        def wrapper(event, context):
            logger.info(context)
            logger.info(event)
            if lambda_name not in event.get('skip', []):
                try:
                    log_to_foursight(event, lambda_name)
                except:
                    pass
                return function(event, context)
            else:
                logger.info('skiping %s since skip was set in input_json' % lambda_name)

        return wrapper
    return decorator
