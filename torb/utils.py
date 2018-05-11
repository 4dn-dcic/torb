from __future__ import print_function
import json
import boto3
import os
import mimetypes
import requests
import yaml
from zipfile import ZipFile
from io import BytesIO
from uuid import uuid4
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
