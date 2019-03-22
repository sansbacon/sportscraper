# test_yahoo.py

from pathlib import Path
import pytest
import random

from sportscraper.yahoo import Scraper


@pytest.yield_fixture(scope='session')
def scraper():
    scraper = Scraper(authfn=str(Path.home() / '.auth.json'),
                      sport='nba',
                      game_key=380,
                      yahoo_season=2018)
    yield scraper


def test_game(scraper):
    '''

    '''
    scraper.response_format = {'format': 'xml'}
    for game_subresource in ['metadata', 'stat_categories']:
        content = scraper.game(subresource=game_subresource)
        print(game_subresource)
        assert isinstance(content, str)


def test_games(scraper):
    '''

    '''
    scraper.response_format = {'format': 'xml'}
    for game_subresource in ['metadata', 'stat_categories']:
        content = scraper.games(subresource=game_subresource)
        print(game_subresource)
        assert isinstance(content, str)


def test_league(scraper):
    '''

    '''
    scraper.response_format = {'format': 'xml'}
    content = scraper.league(league_id=49127)
    assert isinstance(content, str)


def test_leagues(scraper):
    '''

    '''
    scraper.response_format = {'format': 'xml'}
    league_key = scraper._league_key(49127)
    content = scraper.leagues(league_keys=[league_key])
    assert isinstance(content, str)


def test_player(scraper):
    '''

    '''
    scraper.response_format = {'format': 'xml'}
    player_keys = ['385.p.5007', '385.p.4563', '385.p.5185',
                   '385.p.4612', '385.p.5432', '385.p.4244',
                   '385.p.5007', '385.p.4563', '385.p.5185',
                   '385.p.4612', '385.p.5432', '385.p.4244',
                   '385.p.3704', '385.p.5163', '385.p.4487',
                   '385.p.6018', '385.p.5822', '385.p.5768',
                   '385.p.5769', '385.p.5323', '385.p.5667']
    content = scraper.player(player_key=random.choice(player_keys))
    assert isinstance(content, str)
    assert 'player' in content


def test_players(scraper):
    '''

    '''
    scraper.response_format = {'format': 'xml'}
    player_keys = ['385.p.5007', '385.p.4563', '385.p.5185',
                   '385.p.4612', '385.p.5432', '385.p.4244',
                   '385.p.5007', '385.p.4563', '385.p.5185',
                   '385.p.4612', '385.p.5432', '385.p.4244',
                   '385.p.3704', '385.p.5163', '385.p.4487',
                   '385.p.6018', '385.p.5822', '385.p.5768',
                   '385.p.5769', '385.p.5323', '385.p.5667']
    content = scraper.players(player_keys=random.sample(player_keys, 3))
    assert isinstance(content, str)
    assert 'player' in content


def test_roster(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    team_keys = ['385.l.49127.t.1', '385.l.49127.t.6', '385.l.49127.t.5',
                 '385.l.49127.t.7', '385.l.49127.t.2', '385.l.49127.t.9',
                 '385.l.49127.t.4', '385.l.49127.t.3', '385.l.49127.t.8']
    content = scraper.roster(team_key=random.choice(team_keys))
    assert isinstance(content, str)
    assert 'team' in content


def test_team(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    team_keys = ['385.l.49127.t.1', '385.l.49127.t.6', '385.l.49127.t.5',
                 '385.l.49127.t.7', '385.l.49127.t.2', '385.l.49127.t.9',
                 '385.l.49127.t.4', '385.l.49127.t.3', '385.l.49127.t.8']
    content = scraper.team(team_key=random.choice(team_keys))
    assert isinstance(content, str)
    assert 'team' in content


def test_teams(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    team_keys = ['385.l.49127.t.1', '385.l.49127.t.6', '385.l.49127.t.5',
                 '385.l.49127.t.7', '385.l.49127.t.2', '385.l.49127.t.9',
                 '385.l.49127.t.4', '385.l.49127.t.3', '385.l.49127.t.8']
    content = scraper.teams(team_keys=random.sample(team_keys, 2))
    assert isinstance(content, str)
    assert 'team' in content


def test_transactions(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    content = scraper.transactions(league_id=49127)
    assert isinstance(content, str)
    assert 'transaction' in content


def test_user(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    content = scraper.user()
    assert isinstance(content, str)
    assert 'user' in content


def test_users(scraper):
    '''

    Args:
        scraper:

    Returns:

    '''
    content = scraper.users()
    assert isinstance(content, str)
    assert 'user' in content
