====
torb
====


Repository Superseded
=====================

The entire torb repository has been superseded.


Original Purpose
----------------

Torbjörn was the builder bot that built our application and handled automated deployment.
It used AWS Step Functions to orchestrate a number of individual lambda functions that
controlled the various steps required for deployment and management of our ElasticBeanstalk
servers.


Replacement
------------

Our Docker-based servers are now deployed and managed through orchestrated AWS Fargate/ECS services.
Some automation of our production docker image builds happens in CodeBuild.
Some deployment operations are available via our Foursight application.


Final Version
-------------

The penultimate version of the code, should any historians care, was at git tag ``v1.999``.
But to avoid confusion, we've deleted all that for this final version.
