from torb.create_beanstalk.service import handler as creator
import pytest


@pytest.fixture
def bs_json():
    return {
      "source_env": "fourfront-webdev",
      "dest_env": "fourfront-staging",
      "dry_run": False,
      "merge_into": "production",
      "repo_owner": "4dn-dcic",
      "repo_name": "fourfront",
      "branch": "master",
      "_overrides": [
        {
          "waitfor_details": "fourfront-staging.co3gwj7b7tpq.us-east-1.rds.amazonaws.com",
          "type": "create_rds",
          "id": "fourfront-staging",
          "dry_run": False
        },
        {
          "waitfor_details": "search-fourfront-staging-oqzeugqyyqvgdapb46slrzq5ha.us-east-1.es.amazonaws.com:80",
          "type": "create_es",
          "id": "fourfront-staging",
          "dry_run": False
        },
        None,
        {
          "source_env": "fourfront-webdev",
          "dest_env": "fourfront-staging",
          "dry_run": False,
          "merge_into": "production",
          "repo_owner": "4dn-dcic",
          "repo_name": "fourfront",
          "branch": "master"
        }
      ]
    }


def test_can_we_get_bs_url(bs_json):
    pass
    # assert creator(bs_json, 1)
