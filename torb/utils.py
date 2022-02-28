import requests
import yaml
import os
import json
import logging
from dcicutils.beanstalk_utils import log_to_foursight

########################################
# These utils exclusively live in Torb #
########################################

logger = logging.getLogger(__name__)


raise AssertionError("The 'torb' repository is no longer supported.")


def get_default(data, key, default=None):
    return data.get(key, os.environ.get(key, default))


def get_travis_config(branch='master', repo='fourfront', gh_user='4dn-dcic', filename='.travis.yml'):
    """
    Pull the travis config YAML from github
    """
    fourfront_travis_yml_url = 'https://raw.githubusercontent.com/{}/{}/{}/{}'.format(gh_user, repo, branch, filename)
    return yaml.safe_load(requests.get(fourfront_travis_yml_url).content)


def kick_travis_build(branch, repo_owner, repo_name, env, travis_key=None):
    """
    if getting permission errors, it is likely due to an outdated travis
    access key. For more information and instructions on how to generate one,
    see: https://docs.travis-ci.com/user/triggering-builds
    """
    print("trigger build for %s/%s on branch %s" % (repo_owner, repo_name, branch))

    if travis_key is None:
        travis_key = os.environ.get('travis_key')

    # overwrite the before_install section (travis doesn't allow append)
    # by adding the tibanna-deploy env variable, which will trigger the deploy
    body = {
        "request": {
            "message": "kick_travis_build: Torb triggered build to %s has started" % env,
            "branch": branch,
            "config": {
                "before_install":
                    (
                        ["export tibanna_deploy=" + env]
                        + get_travis_config(branch, repo_name, repo_owner).get('before_install', [])
                    )
            }
        }
    }

    headers = {
        'Content-Type': 'application/json',
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
    except Exception:
        pass

    return resp


def powerup(lambda_name):
    '''
    Decorator used for wrapping the service functions for lambdas.
    Takes care of logging, skipping lambas by name using the `skip` key in
    input JSON, and logging to Foursight.

    Should be used to decorate the `handler` functions of service.py module
    for lambas that are used within step functions.
    '''
    def decorator(function):
        logging.basicConfig()
        logger = logging.getLogger('logger')

        def wrapper(event, context):
            logger.info(context)
            logger.info(event)
            if lambda_name not in event.get('skip', []):
                # log_to_foursight only PUTs check if '_foursight' in event
                try:
                    log_to_foursight(event, lambda_name)
                except Exception as exc:
                    logger.warning('Error in powerup on bs.log_to_foursight: %s' % exc)
                return function(event, context)
            else:
                logger.info('skipping %s since skip was set in input_json' % lambda_name)

        return wrapper
    return decorator
