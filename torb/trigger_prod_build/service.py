# -*- coding: utf-8 -*-
import boto3
import json
from datetime import datetime
from torb import beanstalk_utils as bs

client = boto3.client('stepfunctions', region_name='us-east-1')
STEP_FUNCTION_ARN = 'arn:aws:states:us-east-1:643366669028:stateMachine:test__prod_deployment'


def handler(event, context):
    '''
    this is triggered on completed file upload from s3 and
    event will be set to file data.
    '''
    # determine if we are deploying to fourfront-webprod or fourfront-webprod2
    event['source_env'] = bs.whodaman().get('EnvironmentName')
    if event['source_env'] == 'fourfront-webprod':
        event['dest_env'] = 'fourfront-webprod2'
    elif event['source_env'] == 'fourfront-webprod2':
        event['dest_env'] = 'fourfront-webprod'

    run_name = "%s_prod_deploy_for_%s" % (event['dest_env'],
                                          datetime.now().strftime("%a_%b_%d_%Y__%H%M%S"))

    # get db_url from source_env
    info = bs.beanstalk_info(event['source_env'])
    event['db_url'] = [setting['Value'] for setting in
                       info['ConfigurationSettings'][0]['OptionSettings']
                       if setting['OptionName'] == 'RDS_HOSTNAME'][0]

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
      "source_env": event.get('source_env') or "fourfront-webprod",
      "dest_env": event.get('dest_env') or "fourfront-webprod2",
      "db_url": event.get('db_url') or '',
      "dry_run": False,
      "repo_owner": "4dn-dcic",
      "repo_name": "fourfront",
      "branch": "production",
      "large_bs": True,
      "load_prod": True,
    }
    return json.dumps(data)
