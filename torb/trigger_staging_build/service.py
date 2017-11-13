# -*- coding: utf-8 -*-
import boto3
import json
from datetime import datetime

client = boto3.client('stepfunctions', region_name='us-east-1')
STEP_FUNCTION_ARN = 'arn:aws:states:us-east-1:643366669028:stateMachine:staging_deployment'


def handler(event, context):
    '''
    this is triggered on completed file upload from s3 and
    event will be set to file data.
    '''
    run_name = "staging_deploy_for_%s" % datetime.now().strftime("%a_%b_%d_%Y__%H%M%S")

    if event.get('run_name'):
        run_name = event.get('run_name')  # used for testing

    # trigger the step function to run
    response = client.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        name=run_name,
        input=make_input(event),
    )

    # pop no json serializable stuff...
    response.pop('startDate')
    return response


def make_input(event):
    data = {
      "source_env": "fourfront-webprod",
      "dest_env": "fourfront-staging",
      "dry_run": False,
      "merge_into": "production",
      "repo_owner": "4dn-dcic",
      "repo_name": "fourfront",
      "branch": "master",
      "large_bs": True,
      "load_prod": True,
    }
    return json.dumps(data)
