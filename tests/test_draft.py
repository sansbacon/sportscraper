# test_draft.py

import pytest

from sportscraper.draft import Scraper, Parser


@pytest.yield_fixture(scope='session')
def scraper():
    scraper = Scraper(cache_name='test_draft')
    yield scraper

@pytest.yield_fixture(scope='session')
def parser():
    parser = Parser()
    yield parser

def test_complete_contests(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    contests = parser.complete_contests(cc=scraper.complete_contests(),
                                        season_year=2018)
    assert isinstance(contests, list)
    assert isinstance(contests[0], dict)

