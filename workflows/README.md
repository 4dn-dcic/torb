# Step Function Workflows

This directory contains definitions for AWS Step Functions that are created from the lambdas within torb.

JSON events are used throughout the workflows, which are handled in customized ways for the input and output of each steps using `ResultPath`, `InputPath`, and `OutputPath` fields. See [here](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-input-output-filtering.html) for more information. Additionally, the `waitfor` Lambda is used heavily with `Retry` blocks in the workflows; read [the documentation](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html) for details.

### ff_deploy_staging
This step function is for triggering the staging build as part of our blue-green deployment strategy. The two ElasticBeanstalk environments used are "fourfront-webprod" and "fourfront-webprod2".

The best way to trigger this function is to use the `trigger_staging_build` lambda [defined in Torb](../trigger_staging_build/service.py) with an empty JSON event body. Alternatively, there is an [example input JSON](./example_inputs/ff_deploy_staging_sample.json) that contains all the necessary fields for manually triggering the step function -- if going this route, make sure you set the correct `source_env` and `dest_env` values.

### ff_create_env
**TODO: Fix step fxn. Make example input JSON.**
Use this step function to spin up a new Fourfront environment. Right now, this won't work. Need to replace `set-bs-env` with `create-beanstalk`.
