# -*- coding: utf-8 -*-
import os
import errno
import sys
import webbrowser
import json
import requests
import random
from invoke import task, run
import boto3
import contextlib
import shutil
import time
# from botocore.errorfactory import ExecutionAlreadyExists
from contextlib import contextmanager
import aws_lambda
from dcicutils import beanstalk_utils as bs

docs_dir = 'docs'
build_dir = os.path.join(docs_dir, '_build')
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


@contextmanager
def setenv(**kwargs):
    # Backup
    prev = {}
    for k, v in kwargs.items():
        if k in os.environ:
            prev[k] = os.environ[k]
        os.environ[k] = v

    yield

    # Restore
    for k in kwargs.keys():
        if k in prev:
            os.environ[k] = prev[k]
        else:
            del os.environ[k]


def get_all_core_lambdas():
    return [
        'travis_deploy_prod',
        'travis_deploy',
        'create_es',
        'create_beanstalk',
        'waitfor',
        'snapshot_rds',
        'create_rds',
        'set_bs_env',
        'update_bs_config',
        'trigger_prod_build',
        'trigger_staging_build'
    ]


@contextlib.contextmanager
def chdir(dirname=None):
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
            yield
    finally:
        os.chdir(curdir)


@task
def loc(ctx):
    """
    Count lines-of-code.
    """
    excludes = ['/tests/', '/Data_files', 'Submit4DN.egg-info', 'docs', 'htmlcov',
                'README.md', 'README.rst', '.eggs']

    run('find . -iname "*py" | grep -v {} | xargs wc -l | sort -n'.format(
        ' '.join('-e ' + e for e in excludes)))


def copytree(src, dst, symlinks=False, ignore=None):
    skipfiles = ['.coverage', 'dist', 'htmlcov', '__init__.pyc', 'coverage.xml', 'service.pyc']
    for item in os.listdir(src):
        src_file = os.path.join(src, item)
        dst_file = os.path.join(dst, item)
        if src_file.split('/')[-1] in skipfiles:
            print("skipping file %s" % src_file)
            continue
        if os.path.isdir(src_file):
            mkdir(dst_file)
            shutil.copytree(src_file, dst_file, symlinks, ignore)
        else:
            shutil.copy2(src_file, dst_file)


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


@task
def new_lambda(ctx, name, base='create_beanstalk'):
    '''
    create a new lambda by copy from a base one and replacing some core strings.
    '''
    src_dir = './torb/%s' % base
    dest_dir = './torb/%s' % name
    mkdir(dest_dir)
    copytree(src=src_dir, dst=dest_dir)
    chdir(dest_dir)
    # TODO: awk some lines here...


@task(aliases=['tests'])
def test(ctx, watch=False, last_failing=False, no_flake=False, k='',  extra=''):
    """
    Run flake and the tests. Set no_flake to true to skip flake. Any value
    provided to `k` parameter will be passed to "pytest -k <value>"
    Note: --watch requires pytest-xdist to be installed.
    """
    import pytest
    if not no_flake:
        flake(ctx)
    args = ['-rxs', ]
    if k:
        args.append('-k %s' % k)
    args.append(extra)
    if watch:
        args.append('-f')
    if last_failing:
        args.append('--lf')
    retcode = pytest.main(args)
    if retcode != 0:
        print("test failed exiting")
        sys.exit(retcode)
    return(retcode)


@task
def flake(ctx):
    """Run flake8 on codebase."""
    run('flake8 .', echo=True)
    print("flake8 passed!!!")


@task
def clean(ctx):
    run("rm -rf build")
    run("rm -rf dist")
    print("Cleaned up.")


@task
def deploy(ctx, name, version=None, no_tests=False):
    """
    Deploy lambdas, given by `name` parameter. Use 'all' or 'devops' to deploy
    custom lists of lambdas (see below)
    """
    print("preparing for deploy...")
    print("make sure tests pass")
    if no_tests is False:
        if test(ctx) != 0:
            print("tests need to pass first before deploy")
            return
    if name == 'all':
        names = get_all_core_lambdas()
        print(names)
    elif name == 'devops':
        names = [
            'travis_deploy',
            'create_es',
            'create_beanstalk',
            'waitfor',
            'snapshot_rds',
            'create_rds',
            'update_bs_config',
        ]
    else:
        names = [name, ]

    # dist directores are the enemy, clean them all
    for name in get_all_core_lambdas():
        print("Cleaning all lambda builds before deploying...")
        with chdir("./torb/%s" % (name)):
            clean(ctx)

    for name in names:
        print("=" * 20, "Deploying lambda", name, "=" * 20)
        with chdir("./torb/%s" % (name)):
            print("Cleaning up previous build...")
            clean(ctx)
            print("Building lambda package...")
            deploy_lambda_package(ctx, name)
            # need to clean up all dist, otherwise, installing local package takes forever
            print("Cleaning up deployed build...")
            clean(ctx)
        print("next get version information")
        # version = update_version(ctx, version)
        print("then tag the release in git")
        # git_tag(ctx, version, "new production release %s" % (version))
        # print("Build is now triggered for production deployment of %s "
        #       "check travis for build status" % (version))


@task
def deploy_lambda_package(ctx, name):
    # third part tools, should all be tar
    '''
    tools_dir = os.path.join(ROOT_DIR, "third_party")
    bin_dir = os.path.join(ROOT_DIR, "bin")

    for filename in os.listdir(tools_dir):
        if filename.endswith('.tar'):
            fullpath = os.path.join(tools_dir, filename)
            run("tar -xvf %s -C %s" % (fullpath, bin_dir))
    '''

    aws_lambda.deploy(os.getcwd(), local_package='../..', raw_copy='../../bin',
                      requirements='../../requirements.txt')


@task
def update_version(ctx, version=None):
    """
    CURRENTLY NOT USED
    Would be used to update _version.py if we decide to package torb
    """
    from torb._version import __version__
    print("Current version is ", __version__)
    if version is None:
        version = input("What version would you like to set for new release (please use x.x.x / "
                        " semantic versioning): ")

    # read the versions file
    lines = []
    with open("wranglertools/_version.py") as readfile:
        lines = readfile.readlines()

    if lines:
        with open("wranglertools/_version.py", 'w') as writefile:
            lines[-1] = '__version__ = "%s"\n' % (version.strip())
            writefile.writelines(lines)

    run("git add wranglertools/_version.py")
    run("git commit -m 'version bump'")
    print("version updated to", version)
    return version


@task
def git_tag(ctx, tag_name, msg):
    """
    CURRENTLY NOT USED
    Would be used to tag a git release if we decide to package torb
    """
    run('git tag -a %s -m "%s"' % (tag_name, msg))
    run('git push --tags')
    run('git push')


@task
def clean_docs(ctx):
    run("rm -rf %s" % build_dir, echo=True)


@task
def browse_docs(ctx):
    path = os.path.join(build_dir, 'index.html')
    webbrowser.open_new_tab(path)


@task
def docs(ctx, clean=False, browse=False, watch=False):
    """Build the docs."""
    if clean:
        clean_docs(ctx)
    run("sphinx-build %s %s" % (docs_dir, build_dir), echo=True)
    if browse:
        browse_docs(ctx)
    if watch:
        watch_docs(ctx)


@task
def watch_docs(ctx):
    """Run build the docs when a file changes."""
    try:
        import sphinx_autobuild  # noqa
    except ImportError:
        print('ERROR: watch task requires the sphinx_autobuild package.')
        print('Install it with:')
        print('    pip install sphinx-autobuild')
        sys.exit(1)
    run('sphinx-autobuild {0} {1} --watch {2}'.format(
        docs_dir, build_dir, '4DNWranglerTools'), echo=True, pty=True)


@task
def publish(ctx, test=False):
    """
    NOT CURRENTLY USED
    Publish this package to pypi.
    """
    clean(ctx)
    if test:
        run('python setup.py register -r test sdist bdist_wheel', echo=True)
        run('twine upload dist/* -r test', echo=True)
    else:
        run('python setup.py register sdist bdist_wheel', echo=True)
        run('twine upload dist/*', echo=True)


@task
def travis(ctx, branch='production', owner='4dn-dcic', repo_name='fourfront'):
    # lambdas use logging
    import logging
    logging.basicConfig()

    from torb.travis_deploy.service import handler as travis
    data = {'branch': branch,
            'repo_owner': owner,
            'repo_name': repo_name
            }
    travis(data, None)
    # print("https://travis-ci.org/%s" % res.json()['repository']['slug'])


@task
def swap_cname(ctx, src, dest):
    print("=" * 20, "Deploying CNAMEs", "=" * 20)
    bs.swap_cname(src, dest)
    print("Giving CNAMEs 10 seconds to update...")
    time.sleep(10)
    print("Now updating foursight environments...")
    # handle switching foursight environments for data/staging
    res_data = bs.create_foursight_auto(src)
    print('Updated foursight %s environment to use %s. Foursight response: %s'
          % (res_data['fs_url'], res_data['dest_env'], res_data['foursight']))
    res_stag = bs.create_foursight_auto(dest)
    print('Updated foursight %s environment to use %s. Foursight response: %s'
          % (res_stag['fs_url'], res_stag['dest_env'], res_stag['foursight']))


@task
def deploy_workflow(ctx):
    """
    Deploy a Torb step function by name
    See https://github.com/4dn-dcic/tibanna/blob/master/core/utils.py#L317
    """
    raise NotImplementedError


@task
def run_workflow(ctx):
    """
    Trigger a Torb step function by name, with direct input JSON or a filepath.
    See https://github.com/4dn-dcic/tibanna/blob/master/core/utils.py#L230
    """
    # client = boto3.client('stepfunctions', region_name='us-east-1')
    # # maybe make a function in dcicutils.sfn_utils to get ARN by name?
    # STEP_FUNCTION_ARN = ...
    # response = client.start_execution(
    #     stateMachineArn=STEP_FUNCTION_ARN,
    #     name=run_name,
    #     input=make_input(event),
    # )
    raise NotImplementedError
