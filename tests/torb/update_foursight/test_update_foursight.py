from torb.update_foursight import service
import pytest
import mock
from torb.beanstalk_utils import create_foursight_auto


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


@mock.patch('torb.beanstalk_utils.get_beanstalk_real_url', return_value='https://data.4dnucleome.org')
@mock.patch('torb.beanstalk_utils.get_es_from_bs_config', return_value='fake_es_url')
@mock.patch('torb.beanstalk_utils.create_foursight')
def test_create_foursight_auto_prod(mock_fs, mock_es, mock_bs, bs_prod_json):
    expected = {'bs_url': 'https://data.4dnucleome.org',
                'dest_env': 'fourfront-webprod',
                'es_url': 'fake_es_url',
                'fs_url': 'data'
                }

    create_foursight_auto(bs_prod_json['dest_env'])
    mock_bs.assert_called_once()
    mock_es.assert_called_once_with(expected['dest_env'])
    mock_fs.assert_called_once_with(**expected)


@mock.patch('torb.beanstalk_utils.get_beanstalk_real_url', return_value='http://staging.4dnucleome.org')
@mock.patch('torb.beanstalk_utils.get_es_from_bs_config', return_value='fake_es_url')
@mock.patch('torb.beanstalk_utils.create_foursight')
def test_create_foursight_auto_staging_env(mock_fs, mock_es, mock_bs, bs_prod_json):
    expected = {'bs_url': 'http://staging.4dnucleome.org',
                'dest_env': 'fourfront-webprod',
                'es_url': 'fake_es_url',
                'fs_url': 'staging'
                }

    create_foursight_auto(bs_prod_json['dest_env'])
    mock_bs.assert_called_once()
    mock_es.assert_called_once_with(expected['dest_env'])
    mock_fs.assert_called_once_with(**expected)


@mock.patch('torb.beanstalk_utils.get_beanstalk_real_url',
            return_value='fourfront-mastertest.9wzadzju3p.us-east-1.elasticbeanstalk.com')
@mock.patch('torb.beanstalk_utils.get_es_from_bs_config', return_value='fake_es_url')
@mock.patch('torb.beanstalk_utils.create_foursight')
def test_create_foursight_auto_with_dev_env(mock_fs, mock_es, mock_bs, bs_json):
    expected = {'bs_url': 'fourfront-mastertest.9wzadzju3p.us-east-1.elasticbeanstalk.com',
                'dest_env': 'fourfront-mastertest',
                'es_url': 'fake_es_url',
                'fs_url': 'fourfront-mastertest'
                }

    service.handler(bs_json, 0)
    mock_bs.assert_called_once()
    mock_es.assert_called_once_with(expected['dest_env'])
    mock_fs.assert_called_once_with(**expected)


@mock.patch('torb.update_foursight.service.bs.create_foursight_auto')
def test_update_foursight_calls_auto_staging(mock_create):

    service.handler({'dest_env': 'staging'}, 1)
    mock_create.assert_called_once_with('staging')
