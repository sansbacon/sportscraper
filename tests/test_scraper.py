# test_scraper.py

import os
import pytest

from sportscraper.scraper import RequestScraper, BrowserScraper


@pytest.yield_fixture(scope='session')
def scraper():
    scraper = RequestScraper(cache_name='test_rs')
    yield scraper

@pytest.yield_fixture(scope='session')
def bscraper():
    bscraper = BrowserScraper(profile=os.getenv('FIREFOX_PROFILE'))
    yield bscraper
    bscraper.__del__()

def test_rget(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    url = 'https://www.google.com'
    content = scraper.get(url)
    assert isinstance(content, str)
    assert 'Google' in content

def test_rget_json(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    url = 'https://api.bitbucket.org/2.0/users/karllhughes'
    content = scraper.get_json(url)
    assert isinstance(content, dict)
    assert content.get('username') is not None

def test_bget(bscraper):
    '''

    Args:
        bscraper:

    Returns:

    '''
    url = 'https://www.google.com'
    content = bscraper.get(url)
    assert isinstance(content, str)
    assert 'Google' in content

def test_bget_json(bscraper):
    '''

    Args:
        bscraper:

    Returns:

    '''
    url = 'https://api.bitbucket.org/2.0/users/karllhughes'
    content = bscraper.get_json(url)
    assert isinstance(content, dict)
    assert content.get('username') is not None
