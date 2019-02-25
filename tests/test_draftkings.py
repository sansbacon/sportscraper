# test_draftkings.py

import os
import pytest
import random

from sportscraper.draftkings import Scraper, BScraper, Parser, Agent


@pytest.yield_fixture(scope='session')
def scraper():
    scraper = Scraper(cache_name='test_draftkings')
    yield scraper

@pytest.yield_fixture(scope='session')
def bscraper():
    bscraper = BScraper(profile=os.getenv('FIREFOX_PROFILE'))
    yield bscraper
    bscraper.__del__()

@pytest.yield_fixture(scope='session')
def parser():
    parser = Parser()
    yield parser

@pytest.yield_fixture(scope='session')
def agent():
    agent = Agent(cache_name='dk-agent',
                  profile=os.getenv('FIREFOX_PROFILE'))
    yield agent
    agent.bscraper.__del__()

@pytest.yield_fixture(scope='session')
def draft_group_id(scraper, parser):
    '''
    Gets a draft group ID from lobby

    Args:
        scraper:
        parser:

    Returns:
        int

    '''
    contests = parser.contests(scraper.contests())
    draft_group_id = random.choice(contests).get('draft_group_id')
    yield draft_group_id

def test_contests(scraper, parser):
    '''

    Args:
        scraper:
        parser:

    Returns:

    '''
    contests = parser.contests(scraper.contests())
    assert isinstance(contests, list)
    assert isinstance(contests[0], dict)

def test_draftables(scraper, parser, draft_group_id):
    '''

    Args:
        scraper:
        parser:
        draft_group_id:

    Returns:

    '''
    draftables = parser.draftables(scraper.draftables(draft_group_id))
    assert isinstance(draftables, list)
    assert isinstance(draftables[0], dict)

def test_salaries(scraper, parser, draft_group_id):
    '''

    Args:
        scraper:
        parser:
        draft_group_id:

    Returns:

    '''
    salaries = parser.salaries(scraper.salaries(draft_group_id))
    assert draft_group_id > 0
    assert isinstance(salaries, list)
    assert isinstance(salaries[0], dict)

