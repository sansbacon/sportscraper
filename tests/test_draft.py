# test_draft.py

import os
import pytest
import random

from sportscraper.draft import Scraper, Parser


@pytest.yield_fixture(scope='session')
def scraper():
    scraper = Scraper(cache_name='scraper-cache')
    yield scraper


@pytest.yield_fixture(scope='session')
def parser():
    parser = Parser()
    yield parser


def test_bestball_ownership(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    own = parser.bestball_ownership(scraper.bestball_ownership(window_cluster_id=2743))
    assert isinstance(own, list)
    assert isinstance(random.choice(own), dict)


def test_clustered_complete_contests(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    contest_ids = parser.clustered_complete_contests(scraper.clustered_complete_contests())
    assert isinstance(contest_ids, list)
    assert isinstance(random.choice(contest_ids), int)


def test_complete_contests(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    contests = parser.complete_contests(scraper.complete_contests(window_cluster_id=2743))
    assert isinstance(contests, list)
    assert contests[0].get('prize') is not None


def test_clustered_results(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    results = parser.clustered_results(scraper.clustered_results(user_id=os.getenv('DRAFT_USER_ID')))
    assert isinstance(results, list)
    assert isinstance(random.choice(results), dict)


def test_results(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    results = parser.results(scraper.results(window_cluster_id=2015))
    assert isinstance(results, list)
    assert isinstance(random.choice(results), dict)


def test_player_pool(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    pool = parser.player_pool(scraper.player_pool(15035), '2019-02-21')
    assert isinstance(pool, list)
    assert isinstance(random.choice(pool), dict)

