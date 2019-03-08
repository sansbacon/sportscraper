# test_draft.py

import pytest
import random

from sportscraper.draft import Scraper, Parser
from sportscraper.testconf import *


@pytest.yield_fixture(scope='session')
def scraper():
    scraper = Scraper(cache_name='test-draft')
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
    own = parser.bestball_ownership(
        scraper.bestball_ownership(window_cluster_id=window_cluster_id_curr))
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
    contests = parser.complete_contests(
        scraper.complete_contests(window_cluster_id=window_cluster_id_curr))
    assert isinstance(contests, list)
    assert contests[0].get('prize') is not None


def test_contest_results(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    contest_metadata, teams, users, weekly_results = parser.contest_results(
        scraper.contest_results(contest_id=random.choice(contest_ids)))
    assert isinstance(contest_metadata, dict)
    assert isinstance(teams, list)
    assert isinstance(weekly_results, list)
    assert isinstance(users, list)


def test_clustered_results(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    results = parser.clustered_results(scraper.clustered_results(
        user_id=draft_user_id))
    assert isinstance(results, list)
    assert isinstance(random.choice(results), dict)


def test_player_pool(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    pool = parser.player_pool(scraper.player_pool(player_pool_id),
                              player_pool_date)
    assert isinstance(pool, list)
    assert isinstance(random.choice(pool), dict)


def test_window_cluster_results(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    results = parser.window_cluster_results(
                scraper.window_cluster_results(window_cluster_id=window_cluster_id))
    assert isinstance(results, list)
    assert isinstance(random.choice(results), dict)
