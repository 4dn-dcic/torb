from torb.utils import log_to_foursight
import pytest


@pytest.fixture
def fs_event():
    return {"_foursight": {"check": "staging/staging_deployment",
                           "log_desc": "test staging build"
                           }
            }


def test_foursight_logging(fs_event):
    res = log_to_foursight(fs_event, "unittest")
    assert(res)
    assert(res.json())
