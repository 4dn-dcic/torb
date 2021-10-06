# -*- coding: utf-8 -*-
import boto3
import json
from datetime import datetime
from dcicutils import beanstalk_utils as bs

client = boto3.client('stepfunctions', region_name='us-east-1')
STEP_FUNCTION_ARN = 'arn:aws:states:us-east-1:643366669028:stateMachine:ff_deploy_staging'


def handler(event, context):
    '''
    Kick off the ff_deploy_staging step function, which will trigger a staging
    deployment. The ElasticBeanstalk environments for data and staging are
    determined using beanstalk_utils.compute_ff_prd_env, which requires ElasticBeanstalk
    IAM permissions
    '''
    # determine if we are deploying to fourfront-webprod or fourfront-webprod2
    event['source_env'] = bs.compute_ff_prd_env()
    if event['source_env'] == 'fourfront-webprod':
        event['dest_env'] = 'fourfront-webprod2'
    elif event['source_env'] == 'fourfront-webprod2':
        event['dest_env'] = 'fourfront-webprod'
    else:
        # event['source_env'] is unexpected. Bail
        return {"type": "trigger_staging_build",
                "torb_message": "invalid event.source_env", "event": event}

    start_time = datetime.now().strftime("%a_%b_%d_%Y__%H%M%S")
    run_name = "%s_deploy_for_%s" % (event['dest_env'], start_time)
    event['start_time'] = start_time

    if event.get('run_name'):
        run_name = event.get('run_name')  # used for testing

    # trigger the step function to run
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        name=run_name,
        input=make_input(event),
    )

    # pop non-JSON serializable stuff...
    response.pop('startDate')
    return response


def make_input(event):
    """
    Generate the event JSON that will passed through the step function.
    A lot of these variables are used when creating/updating the EB environment.
    See: torb/create_beanstalk/service.py for more details
    """
    data = {
      "source_env": event['source_env'],
      "dest_env": event['dest_env'],
      "dry_run": False,
      "merge_into": "production",
      "repo_owner": "4dn-dcic",
      "repo_name": "fourfront",
      "branch": "master",
      "large_bs": True,
      "load_prod": True,
      "_foursight": {
          "check": "staging/staging_deployment",
          "log_desc": "Staging Deployment for %s" % event['start_time'],
       }
    }
    return json.dumps(data)
