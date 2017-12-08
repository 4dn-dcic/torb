from torb.update_foursight import service
import pytest
import mock


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


def test_update_fs_with_prod_env(bs_prod_json):
    expected = {'bs_url': 'https://data.4dnucleome.org',
                'dest_env': 'fourfront-webprod',
                'es_url': 'fake_es_url',
                'fs_url': 'data'
                }

    with mock.patch('torb.update_foursight.service.bs') as mock_bs:
        mock_bs.whodaman.return_value = 'fourfront-webprod'
        mock_bs.get_es_from_health_page.return_value = 'fake_es_url'
        service.handler(bs_prod_json, 0)
        mock_bs.whodaman.assert_called_once()
        mock_bs.get_es_from_health_page.assert_called_once_with(expected['bs_url'])
        mock_bs.create_foursight.assert_called_once_with(**expected)


def test_update_fs_with_staging_env(bs_prod_json):
    expected = {'bs_url': 'http://staging.4dnucleome.org',
                'dest_env': 'fourfront-webprod',
                'es_url': 'fake_es_url',
                'fs_url': 'staging'
                }
    with mock.patch('torb.update_foursight.service.bs') as mock_bs:
        mock_bs.whodaman.return_value = 'fourfront-webprod2'
        mock_bs.get_es_from_health_page.return_value = 'fake_es_url'
        service.handler(bs_prod_json, 0)
        mock_bs.whodaman.assert_called_once()
        mock_bs.get_es_from_health_page.assert_called_once_with(expected['bs_url'])
        mock_bs.create_foursight.assert_called_once_with(**expected)


def test_update_fs_with_dev_env(bs_json):
    expected = {'bs_url': 'fourfront-mastertest.9wzadzju3p.us-east-1.elasticbeanstalk.com',
                'dest_env': 'fourfront-mastertest',
                'es_url': 'fake_es_url',
                'fs_url': 'fourfront-mastertest'
                }

    with mock.patch('torb.update_foursight.service.bs') as mock_bs:
        mock_bs.beanstalk_info.return_value = {'CNAME': expected['bs_url']}
        mock_bs.get_es_from_health_page.return_value = 'fake_es_url'
        service.handler(bs_json, 0)
        mock_bs.beanstalk_info.assert_called_once()
        mock_bs.get_es_from_health_page.assert_called_once_with(expected['bs_url'])
        mock_bs.create_foursight.assert_called_once_with(**expected)
