====
torb
====

.. warning::

  The entire 'torb' repository is no longer supported.

  The actions defined by this repository are no longer
  the proper way to achieve the goals documented here.

  This repository, including the associated documentation that
  you are reading now, is retained only for historical purposes.

.. ifconfig: travis-builds-matter

    .. image:: https://travis-ci.org/4dn-dcic/torb.svg?branch=master
       :target: https://travis-ci.org/4dn-dcic/torb
       :alt: Build Status

.. ifconfig: coveralls-finally-gets-defined

    .. image:: https://coveralls.io/repos/github/4dn-dcic/torb/badge.svg?branch=master
       :target: https://coveralls.io/github/4dn-dcic/torb?branch=master
      :alt: Coverage

.. ifconfig: readthedocs-finally-gets-defined

    .. image:: https://readthedocs.org/projects/torb/badge/?version=latest
       :target: https://torb.readthedocs.io/en/latest/?badge=latest
       :alt: Documentation Status

**Original Purpose**

Torbjörn is the builder bot that builds our application and handles the automated deployment. It uses AWS Step Functions to orchestrate a number of individual lambda functions that control the various steps required for deployment and management of our servers.


Torb Lambda Functions
=====================

For the most part, Torb is defined by a number of lambda functions that are bundled and deployed using our fork of `python-lambda <https://github.com/4dn-dcic/python-lambda>`_.


create_beanstalk
----------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `create-beanstalk`. `Link <./torb/create_beanstalk/>`_.

Workflows: used in `ff_deploy_staging`

Provide a variety of inputs (see service.py) to create a new ElasticBeanstalk (EB) environment or update an existing one. As part of this process, set EB environment variables and a configuration template. Also attempts to PUT a Foursight environment corresponding to the created EB environment.


create_es
---------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `create-es`. `Link <./torb/create_es/>`_.

Workflows: used in `ff_deploy_staging`

Provide input with `dest_env` to create a new Elasticsearch (ES) instance with the given identifier. Can optionally use `force_new_es` to always create a new ES instance, but this should probably not be used, as creating an ES instance by hand is usually the way to go. Updates `id` and `type` in event JSON to coordinate with `waitfor` Lambda.


create_rds
----------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `create-rds`. `Link <./torb/create_rds/>`_.

Workflows: None

Provide input with `dest_env` and `snapshot_arn` to create an RDS instance with the given ID from the given snapshot ARN. If a current instance already exists with that ID, this will delete it. If "fourfront-webprod" is in the ID, will skip this process due to the danger of deleting the production database.


snapshot_rds
------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `snapshot-rds`. `Link <./torb/snapshot_rds/>`_.

Workflows: None

Provide input with `dest_env` and `snapshot_id` to take a snapshot of an RDS instance with the given ID. The snapshot will have the given name and will delete any existing snapshot with that name.


travis_deploy
-------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `travis-deploy`. `Link <./torb/travis_deploy/>`_.

Workflows: used in `ff_deploy_staging`

Start a travis build and leverage the `tibanna_deploy` environment variables for the travis build to deploy to the "fourfront-mastertest" ElasticBeanstalk on a successful build. Can also leverage `merge_to` to merge a given branch into another one at the end of the build. Branches are determined by `event` and `merge_into` in the event JSON; ElasticBeanstalk environment is set with `dest_env`. See the `Fourfront travis config <https://github.com/4dn-dcic/fourfront/blob/d477c04181ff097bfd7fa59092c18e0c13540a90/.travis.yml#L106-L118>`_ and `deploy_beanstalk.py <https://github.com/4dn-dcic/fourfront/blob/master/deploy/deploy_beanstalk.py>`_ for how this is done. This is a bit different from `trigger_mastertest_build` and `trigger_webdev_build`, since it propogates the event output and therefore can be used within a step function. Writes request information to the `travis` subobject in the event. Also updates `id` and `type` in event to coordinate with `waitfor` Lambda.


trigger_mastertest_build
------------------------
Lambda function name: `trigger-mastertest-build`. `Link <./torb/trigger_mastertest_build/>`_.

.. warning::

    Obsolete. See more complete warning at top of file.

Workflows: None

Start a travis build and leverage the `tibanna_deploy` environment variable for the travis build to deploy to the "fourfront-mastertest" ElasticBeanstalk on a successful build. See the `Fourfront travis config <https://github.com/4dn-dcic/fourfront/blob/d477c04181ff097bfd7fa59092c18e0c13540a90/.travis.yml#L106-L118>`_ and `deploy_beanstalk.py <https://github.com/4dn-dcic/fourfront/blob/master/deploy/deploy_beanstalk.py>`_ for how this is done. No information is needed from the lambda event JSON. Almost identical functionality to `trigger_webdev_build`.


trigger_staging_build
---------------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `trigger-staging-build`. `Link <./torb/trigger_staging_build/>`_.

Workflows: triggers `ff_deploy_staging`

Use `dcicutils.beanstalk_utils.compute_ff_prd_env` to determine which environments are data and staging, and kick off the `ff_deploy_staging` step function to make a fresh deploy to staging using Fourfront master. No information is needed from the lambda event JSON.


trigger_webdev_build
--------------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `trigger-webdev-build`. `Link <./torb/trigger_webdev_build/>`_.

Workflows: None

Start a travis build and leverage the `tibanna_deploy` environment variable for the travis build to deploy to the "fourfront-webdev" ElasticBeanstalk on a successful build. See the `Fourfront travis config <https://github.com/4dn-dcic/fourfront/blob/d477c04181ff097bfd7fa59092c18e0c13540a90/.travis.yml#L106-L118>`_ and `deploy_beanstalk.py <https://github.com/4dn-dcic/fourfront/blob/master/deploy/deploy_beanstalk.py>`_ for how this is done. No information is needed from the lambda event JSON. Almost identical functionality to `trigger_mastertest_build`.


update_bs_config
----------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `update-bs-config`. `Link <./torb/update_bs_config/>`_.

Workflows: used in `ff_deploy_staging`

Update the configuration template of an existing ElasticBeanstalk environment. Takes `dest_env`, which is the environment name, and `template`, which is the name of the configuration template. Updates `waitfor_details` in the event JSON. Also updates `id` and `type` in event to coordinate with `waitfor` Lambda.


update_foursight
----------------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `update-foursight`. `Link <./torb/update_foursight/>`_.

Workflows: used in `ff_deploy_staging`

Create a Foursight environment for an ElasticBeanstalk environment and PUT a check result to it. The settings for the Fourfront environment are determined automatically from the EB environment. Takes `dest_env`, which is the environment name.


waitfor
-------

.. warning::

    Obsolete. See more complete warning at top of file.

Lambda function name: `waitfor`. `Link <./torb/waitfor/>`_.

Workflows: used in `ff_deploy_staging`

Used as glue within a workflow by retrying until a specified condition is met using a "checker" function. Leverages the `type` and `item_id` within the event JSON and uses them to determine which checker function is used from a hardcoded list. Updates `waitfor_details` in the event JSON on each run.


Torb Worklows
=============


.. warning::

    Obsolete. See more complete warning at top of file.

Torb also defines workflows that use AWS Step Functions composed of Lambda functions. See `this directory <./workflows/>`_ for more information, as well as workflow definitions and example inputs. In the near future, `deploy_workflow` and `run_workflow` tasks will be created to facilitate easier testing and deployment.
