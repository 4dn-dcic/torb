# -*- coding: utf-8 -*-
import boto3
import json
from datetime import datetime
from dcicutils import beanstalk_utils as bs
from dcicutils.env_utils import is_cgap_env, is_fourfront_env, is_stg_or_prd_env, guess_mirror_env

client = boto3.client('stepfunctions', region_name='us-east-1')
STEP_FUNCTION_ARN = 'arn:aws:states:us-east-1:643366669028:stateMachine:ff_deploy_staging'


def handler(event, context):
    '''
    Kick off the ff_deploy_staging step function, which will trigger a staging
    deployment. The ElasticBeanstalk environments for data and staging are
    determined using beanstalk_utils.whodaman, which requires ElasticBeanstalk
    IAM permissions
    '''
    # determine if we are deploying to a production env
    event['source_env'] = bs.whodaman()
    source_env = event['source_env']
    dest_env = None
    if is_fourfront_env(source_env) and is_stg_or_prd_env(source_env):
        # TODO: Making this cgap-compatible means making an adjustment indicated later in this file. -kmp 10-Apr-2020
        dest_env = guess_mirror_env(source_env)
    if not dest_env:
        # e.g., can get here if:
        #  - source_env is a cgap environment (downstream isn't yet ready for that)
        #  - source_env is not a production environment
        #  - source_env is a production environment with no mirror
        return {"type": "trigger_staging_build",
                "torb_message": "invalid event.source_env", "event": event}
    event['dest_env'] = dest_env

    start_time = datetime.now().strftime("%a_%b_%d_%Y__%H%M%S")
    run_name = "%s_deploy_for_%s" % (dest_env, start_time)
    event['start_time'] = start_time

    if event.get('run_name'):
        run_name = event.get('run_name')  # used for testing

    try:
        input = make_input(event)
    except Exception as e:
        return {
            "type": "trigger_staging_build",
            "torb_message": str(e),
        }

    # trigger the step function to run
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        name=run_name,
        input=input,
    )

    # pop non-JSON serializable stuff...
    response.pop('startDate')
    return response


# TODO: This exception and the infer_repo_from_env function should move to env_utils
#       and unit tests should be added there. Then this could be imported from there.
#       Starting with it here will save us a coordination step. -kmp 10-Apr-2020
class InconsistentEnvironments(Exception):

    def __init__(self, source_env, dest_env):
        message = ("The source_env=%s and dest_env=%s must be both cgap or both fourfront environments."
                   % (source_env, dest_env))
        super(InconsistentEnvironments, self).__init__(message)
        self.source_env = source_env
        self.dest_env = dest_env


def infer_repo_from_env(event):
    source_env = event['source_env']
    dest_env = event['dest_env']
    if is_cgap_env(source_env) and is_cgap_env(dest_env):
        return 'cgap-portal'
    elif is_cgap_env(source_env) and is_cgap_env(dest_env):
        return 'fourfront'
    else:
        raise InconsistentEnvironments(source_env=source_env, dest_env=dest_env)


def make_input(event):
    """
    Generate the event JSON that will passed through the step function.
    A lot of these variables are used when creating/updating the EB environment.
    See: torb/create_beanstalk/service.py for more details
    """
    repo_name = infer_repo_from_env(event)
    data = {
        "source_env": event['source_env'],
        "dest_env": event['dest_env'],
        "dry_run": False,
        "merge_into": "production",
        "repo_owner": "4dn-dcic",
        "repo_name": repo_name,
        "branch": "master",
        "large_bs": True,
        "load_prod": True,
        "_foursight": {
            # TODO: Need to make sure this foursight chalicelib check can handle cgap.
            #       I think this is a dummy check in foursight, but that needs to be confirmed,
            #       or even then at minimum a note needs to be added there saying we're expecting this
            #       needs to handle cgap, not just fourfront.
            #       -kmp 10-Apr-2020
            "check": "staging/staging_deployment",
            "log_desc": "Staging Deployment on %s for %s" % (repo_name, event['start_time']),
        }
    }
    return json.dumps(data)
