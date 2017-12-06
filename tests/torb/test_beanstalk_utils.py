from torb import beanstalk_utils as bs
from torb.waitfor.service import handler as waitfor
import pytest


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


def test_is_indexing_finished():
    # mastertest url
    url = 'http://mastertest.4dnucleome.org'
    try:
        status, details = bs.is_indexing_finished(url)
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
