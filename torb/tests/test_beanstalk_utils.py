from dcicutils import beanstalk_utils as bs
from ..waitfor.service import handler as waitfor
import pytest


@pytest.fixture
def fs_event():
    return {
        "_foursight": {
            "check": "staging/staging_deployment",
            "log_desc": "test staging build"
        }
    }


@pytest.fixture
def waitfor_json():
    return {
      "source_env": "fourfront-webprod",
      "dest_env": "fourfront-staging",
      "dry_run": True,
      "merge_into": "production",
      "repo_owner": "4dn-dcic",
      "repo_name": "fourfront",
      "branch": "master",
      "type": "create_es",
      "id": "fourfront-staging",
      "_foursight": {
          "check": "webprod/staging_deployment",
          "log_desc": "Staging Deployment",
       }
    }


def test_foursight_logging(fs_event):
    overrides = {'status': 'PASS', 'full_output': "this is just a test"}
    res = bs.log_to_foursight(fs_event, "unittest", overrides=overrides)
    assert res['status'] == 'success'
    assert res['updated_content']['full_output'] == overrides['full_output']


def test_is_indexing_finished():
    # mastertest url
    env = 'fourfront-mastertest'
    try:
        status, details = bs.is_indexing_finished(env)
    except bs.WaitingForBoto3 as ex:
        # we get this if the environment is updating
        print(ex)
        assert(True)
        return

    if not status:
        assert(details)  # this is set to zero if there is an error
    else:
        # we expect true when indexing is complete
        assert(status)


def test_powerup_logs_to_foursight(waitfor_json):
    assert waitfor(waitfor_json, 1)


def test_wait_for_travis():
    input_json = {
            "dry_run": False,
            "id": 312587257,  # This 'id' needs a better explanatory comment. -kmp 10-Apr-2020
            "type": "travis",
    }
    print(input_json)
    return
