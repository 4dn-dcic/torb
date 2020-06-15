from ...update_foursight import service
import pytest
import mock
# TODO: This import relates to tests that need to move to dcicutils. See below.
#       These comments will go away when the move is accomplished. -kmp 10-Apr-2020
# from dcicutils.beanstalk_utils import create_foursight_auto


@pytest.fixture
def bs_prod_json():
    return {
      "dest_env": "fourfront-webprod",
      "dry_run": False,
    }


@pytest.fixture
def bs_json():
    return {
      "dest_env": "fourfront-mastertest",
      "dry_run": False,
    }


# TODO: These next two tests (of dcicutils.beanstalk_utils.create_foursight_auto) belong in dcicutils,
#       as they don't test any functionality written in this repo. This isn't the right place to be
#       distrustful. But, moreover, these tests suppose a particular implementation of that function,
#       quite dangerously even, since if that implementation changes, this will execute random pieces
#       of operations on production systems. -kmp 10-Apr-2020
#
#
# @mock.patch('dcicutils.beanstalk_utils.get_beanstalk_real_url', return_value='https://data.4dnucleome.org')
# @mock.patch('dcicutils.beanstalk_utils.get_es_from_bs_config', return_value='fake_es_url')
# @mock.patch('dcicutils.beanstalk_utils.create_foursight')
# def test_create_foursight_auto_prod(mock_fs, mock_es, mock_bs, bs_prod_json):
#     expected = {
#         'bs_url': 'https://data.4dnucleome.org',
#         'dest_env': 'fourfront-webprod',
#         'es_url': 'fake_es_url',
#         'fs_url': 'data'
#     }
#
#     create_foursight_auto(bs_prod_json['dest_env'])
#     mock_bs.assert_called_once()
#     mock_es.assert_called_once_with(expected['dest_env'])
#     mock_fs.assert_called_once_with(**expected)
#
#
# @mock.patch('dcicutils.beanstalk_utils.get_beanstalk_real_url', return_value='http://staging.4dnucleome.org')
# @mock.patch('dcicutils.beanstalk_utils.get_es_from_bs_config', return_value='fake_es_url')
# @mock.patch('dcicutils.beanstalk_utils.create_foursight')
# def test_create_foursight_auto_staging_env(mock_fs, mock_es, mock_bs, bs_prod_json):
#     expected = {
#         'bs_url': 'http://staging.4dnucleome.org',
#         'dest_env': 'fourfront-webprod',
#         'es_url': 'fake_es_url',
#         'fs_url': 'staging'
#     }
#
#     create_foursight_auto(bs_prod_json['dest_env'])
#     mock_bs.assert_called_once()
#     mock_es.assert_called_once_with(expected['dest_env'])
#     mock_fs.assert_called_once_with(**expected)


@mock.patch('dcicutils.beanstalk_utils.get_beanstalk_real_url',
            return_value='fourfront-mastertest.9wzadzju3p.us-east-1.elasticbeanstalk.com')
@mock.patch('dcicutils.beanstalk_utils.get_es_from_bs_config', return_value='fake_es_url')
@mock.patch('dcicutils.beanstalk_utils.create_foursight')
def test_create_foursight_auto_with_dev_env(mock_create_foursight, mock_get_es_from_bs_config,
                                            mock_get_beanstalk_real_url,
                                            bs_json):  # fixture
    expected = {
        'bs_url': 'fourfront-mastertest.9wzadzju3p.us-east-1.elasticbeanstalk.com',
        'dest_env': 'fourfront-mastertest',
        'es_url': 'fake_es_url',
        'fs_url': 'fourfront-mastertest'
    }

    service.handler(bs_json, 0)
    mock_get_beanstalk_real_url.assert_called_once()
    mock_get_es_from_bs_config.assert_called_once_with(expected['dest_env'])
    mock_create_foursight.assert_called_once_with(**expected)


@mock.patch('torb.update_foursight.service.bs.create_foursight_auto')
def test_update_foursight_calls_auto_staging(mock_create_foursight_auto):

    service.handler({'dest_env': 'staging'}, 1)
    mock_create_foursight_auto.assert_called_once_with('staging')
