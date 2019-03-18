# yahoo.py

import base64
import datetime
import json
import logging
import re
import webbrowser
import xml.etree.ElementTree as ET

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):

    def __init__(self, authfn, sport, yahoo_season, game_key=None,
                 response_format='xml', cache_name='yahoo-scraper', **kwargs):
        '''
        Initialize scraper object

        Args:
            authfn (str): path of auth.json file
            sport (str):
            game_key (str):
            yahoo_season (int): '2017-18' season is 2017
            response_format(str): 'json' or 'xml'
            headers (dict): dict of headers
            cookies (obj): cookies object
            cache_name (str):
            expire_hours (int): hours to keep in cache
            as_string (bool): false -> returns parsed json, true -> returns string

        Returns:
            YahooFantasyScraper

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        RequestScraper.__init__(self, cache_name=cache_name, **kwargs)

        self.authfn = authfn
        self.auth_uri = 'https://api.login.yahoo.com/oauth2/request_auth'
        self.response_format = {'format': response_format}
        self.sport = sport
        self.yahoo_season = yahoo_season
        self.token_uri = 'https://api.login.yahoo.com/oauth2/get_token'
        if game_key:
            self.game_key = game_key
        else:
            self.game_key = self._game_key()
        self._load_credentials()
        
    def _filtstr(self, filters):
        '''
        Creates filter string for collection URL

        Args:
            filters (dict): dict of filters

        Returns:
            str

        '''
        vals = ['{}={}'.format(k, filters[k]) for k in sorted(filters.keys())]
        return ';' + ','.join(vals)

    def _game_key(self):
        '''
        Game key for queries

        Args:
            None

        Returns:
            int

        '''
        game_key_d = {'nba': {2017: 375, 2018: 385},
                      'nfl': {2018: 380}}
        return game_key_d.get(self.sport).get(self.yahoo_season)

    def _league_key(self, league_id):
        '''
        League key given league_id

        Args:
            league_id (int):

        Returns:
            str
        '''
        return f'{self.game_key}.l.{league_id}'

    def _load_credentials(self):
        '''
        Loads credentials from file or obtains new token from yahoo!

        Args:
            None

        Returns:
            None

        '''
        # load credentials
        with open(self.authfn) as infile:
            self.auth = json.load(infile)

        # check file for refresh token
        if self.auth.get('refresh_token'):
            self._refresh_credentials()

        # if don't have a refresh token, then request auth
        else:
            params = {'client_id': self.auth['client_id'],
                      'redirect_uri': 'oob',
                      'response_type': 'code',
                      'language': 'en-us'}
            r = self.get(self.auth['auth_uri'], params=params)

            # response url will allow you to plug in code
            i = 1
            while i:
                # you may need to add export BROWSER=google-chrome to .bashrc
                webbrowser.open(url=r.url)
                code = input('Enter code from url: ')
                i = 0

            # now get authorization token
            hdr = self.auth_header
            body = {'grant_type': 'authorization_code', 'redirect_uri': 'oob', 'code': code}
            headers = {'Authorization': hdr,
                       'Content-Type': 'application/x-www-form-urlencoded'}
            r = self.post(self.token_uri, data=body, headers=headers)

            # add the token to auth
            context = self.auth.copy()
            context.update(r.json())
            self.auth = context

            # now write back to file
            with open(self.authfn, 'w') as outfile:
                json.dump(self.auth, outfile)

    def _refresh_credentials(self):
        '''
        Refreshes yahoo token

        Returns:
            None

        '''
        body = {'grant_type': 'refresh_token', 'redirect_uri': 'oob', 'refresh_token': self.auth['refresh_token']}
        headers = {'Authorization': self.auth_header,
                   'Content-Type': 'application/x-www-form-urlencoded'}
        r = self.post(self.token_uri, data=body, headers=headers)

        # add the token to auth and write back to file
        context = self.auth.copy()
        context.update(r.json())
        self.auth = context
        with open(self.authfn, 'w') as outfile:
            json.dump(self.auth, outfile)

    def _yahoo_season(self, yahoo_season):
        '''

        Args:
            yahoo_season (int):

        Returns:
            None

        '''
        if not yahoo_season:
            d = datetime.datetime.now()
            y = d.year
            m = d.month
            if m >= 9:
                return y
            return y - 1
        return yahoo_season

    @property
    def auth_header(self):
        '''
        Basic authorization header

        Args:
            None

        Returns:
            str

        '''
        string = '%s:%s' % (self.auth['client_id'], self.auth['client_secret'])
        base64string = base64.standard_b64encode(string.encode('utf-8'))
        return "Basic %s" % base64string.decode('utf-8')

    @property
    def game_subresources(self):
        '''
        Valid game subresources

        Args:
            None

        Returns:
            list

        '''
        return ['metadata', 'leagues', 'players', 'game_weeks',
                'stat_categories', 'position_types', 'roster_positions']

    @property
    def games_subresources(self):
        '''
        Valid games subresources

        Args:
            None

        Returns:
            list

        '''
        return ['metadata', 'leagues', 'players', 'game_weeks',
                'stat_categories', 'position_types', 'roster_positions', 'teams']

    @property
    def games_filters(self):
        '''
        Valid games filters

        Args:
            None

        Returns:
            list

        '''
        return ['is_available', 'game_types', 'game_codes', 'seasons']

    @property
    def league_subresources(self):
        '''
        Valid league subresources

        Args:
            None

        Returns:
            list

        '''
        return ['metadata', 'settings', 'standings', 'scoreboard', 'teams',
                'players', 'draftresults', 'transactions']

    @property
    def leagues_subresources(self):
        '''
        Valid leagues subresources

        Args:
            None

        Returns:
            list

        '''
        return self.league_subresources

    @property
    def player_subresources(self):
        '''
        Valid player subresources

        Args:
            None

        Returns:
            list

        '''
        return ['metadata', 'stats', 'ownership', 'percent_owned', 'draft_analysis']

    @property
    def players_filters(self):
        '''
        Valid players filters

        Args:
            None

        Returns:
            list

        '''
        # for football, replace sort_date with sort_week
        return ['position', 'status', 'search', 'sort', 'sort_type', 'sort_season',
                'sort_date', 'start', 'count']

    @property
    def players_subresources(self):
        '''
        Valid player subresources

        Args:
            None

        Returns:
            list

        '''
        return self.player_subresources

    @property
    def roster_subresources(self):
        '''
        Valid roster subresources

        Args:
            None

        Returns:
            list

        '''
        return ['players']

    @property
    def team_subresources(self):
        '''
        Valid team subresources

        Args:
            None

        Returns:
            list

        '''
        return ['metadata', 'stats', 'standings', 'roster', 'draftresults', 'matchups']

    @property
    def teams_subresources(self):
        '''
        Valid team subresources

        Args:
            None

        Returns:
            list

        '''
        return self.team_subresources

    @property
    def transaction_filters(self):
        '''
        Valid transaction filters

        Args:
            None

        Returns:
            list

        '''
        return ['type', 'types', 'team_key', 'count']

    @property
    def transactions_filters(self):
        '''
        Valid transaction filters

        Args:
            None

        Returns:
            list

        '''
        return self.transaction_filters

    @property
    def transaction_subresources(self):
        '''
        Valid transaction subresources

        Args:
            None

        Returns:
            list

        '''
        return ['metadata', 'players']

    @property
    def transactions_subresources(self):
        '''
        Valid transactions subresources

        Args:
            None

        Returns:
            list

        '''
        return self.transaction_subresources

    @property
    def user_subresources(self):
        '''
        Valid team subresources

        Args:
            None

        Returns:
            list

        '''
        return [None, 'leagues', 'teams']

    @property
    def users_subresources(self):
        '''
        Valid users subresources

        Args:
            None

        Returns:
            list

        '''
        return self.user_subresources

    # methods
    def game(self, subresource='metadata', keys=None):
        '''
        Gets game resource
        https://developer.yahoo.com/fantasysports/guide/game-resource.html

        Args:
            subresource (str): default 'metadata'
            filters (dict):
            keys (list):

        Returns:
            dict: parsed json

        '''
        if subresource not in self.game_subresources:
            raise ValueError('invalid game subresource')
        elif subresource in ['leagues', 'players']:
            if not keys:
                raise ValueError('cannot get subresource {} without keys'.format(subresource))
            elif subresource == 'leagues':
                url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/{}/{};league_keys={}'
                return self.query(url.format(self.sport, subresource, ','.join(keys)))
            elif subresource == 'players':
                url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/{}/{};player_keys={}'
                return self.query(url.format(self.sport, subresource, ','.join(keys)))
        else:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/game/{}/{}'
            return self.query(url.format(self.sport, subresource))

    def games(self, subresource='metadata', filters=None, keys=None):
        '''
        Gets games collection
        https://developer.yahoo.com/fantasysports/guide/games-collection.html

        Args:
            subresource (str): default 'metadata'
            filters (dict):
            keys (list):

        Returns:
            dict: parsed json

        '''
        # games adds an additional subresource for teams
        if subresource not in self.games_subresources:
            raise ValueError('invalid game subresource')
        elif filters:
            if set(filters.keys()) <= set(self.games_filters):
                url = 'https://fantasysports.yahooapis.com/fantasy/v2/games;{}'
                return self.query(url.format(self._filtstr(filters)))
            else:
                raise ValueError('games invalid filters: {}'.format(filters))
        elif subresource == 'leagues':
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/games;game_keys={}/leagues;league_keys={}'
            return self.query(url.format(self.game_key, ','.join(keys)))
        elif subresource == 'players':
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/games;game_keys={}/players;player_keys={}'
            return self.query(url.format(self.game_key, ','.join(keys)))
        else:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/games;game_keys={}/{}'
            return self.query(url.format(self.game_key, subresource))

    def league(self, league_id, subresource='metadata'):
        '''
        Gets league resource
        https://developer.yahoo.com/fantasysports/guide/league-resource.html

        Args:
            league_id (int): id for your league
            subresource (str): metadata, settings, standings, scoreboard, etc.

        Returns:
            dict: parsed json

        '''
        if subresource not in self.league_subresources:
            raise ValueError('invalid subresource')
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}/{}'
        return self.query(url.format(self._league_key(league_id), subresource))

    def leagues(self, league_keys, subresource='metadata'):
        '''
        Gets leagues collection
        https://developer.yahoo.com/fantasysports/guide/leagues-collection.html

        Args:
            league_keys (list): of str (e.g. '375.l.10000')
            subresource (str): default 'metadata'

        Returns:
            dict: parsed json

        '''
        # games adds an additional subresource for teams
        if subresource not in self.league_subresources:
            raise ValueError('invalid league subresource')
        elif league_keys:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/leagues;league_keys={}/{}'
            return self.query(url.format(','.join(league_keys), subresource))

    def player(self, player_key, subresource='metadata'):
        '''
        Gets player resource
        https://developer.yahoo.com/fantasysports/guide/player-resource.html

        Args:
            player_key (str): {game_key}.p.{player_id}

        Returns:
            dict: parsed json

        '''
        if subresource not in self.player_subresources:
            raise ValueError('invalid player subresource')
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/player/{}/{}'
        return self.query(url.format(player_key, subresource))

    def players(self, league_id=None, league_ids=None, team_key=None, team_keys=None,
                player_keys=None, subresource='metadata', filters=None):
        '''
        Gets players collection

        Args:
            league_id (int): id for your league, default None
            league_ids (list): ids for your league, default None
            team_key (str): default None
            team_keys (list): default None
            player_keys (list): default None
            subresource (str): 'metadata', etc.
            filters (dict): default None

        Returns:
            dict: parsed json

        '''
        # construct the URL from the relevant id or key
        if league_id:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/' + self._league_key(league_id) + \
                  '/players{}/{}'
        elif league_ids:
            league_keys = [self._league_key(lid) for lid in league_ids]
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/leagues;league_keys=' + \
                  ','.join(league_keys) + '/players{}/{}'
        elif team_key:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/' + team_key + '/players{}/{}'
        elif team_keys:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/teams;team_keys=' + \
                  ','.join(team_keys) + '/players{}/{}'
        elif player_keys:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/players;player_keys=' + \
                  ','.join(player_keys) + '{}/{}'
        else:
            raise ValueError('must specify one of: league_id, league_ids, team_key, team_keys, player_keys')

        # add filters to the url
        if filters:
            if set(filters.keys()) <= set(self.players_filters):
                return self.query(url.format(self._filtstr(filters), subresource))
            else:
                raise ValueError('games invalid filters: {}'.format(filters))
        else:
            return self.query(url.format('', subresource))

    def query(self, url):
        '''
        Query yahoo API

        '''
        hdr = {'Authorization': 'Bearer %s' % self.auth['access_token']}
        if self.response_format == 'json':
            content = self.get_json(url, headers=hdr, params=self.response_format)
            if 'error' in content:
                # if get error for valid credentials, refresh and try again
                desc = content['error']['description']
                if 'Please provide valid credentials' in desc:
                    self._refresh_credentials()
                    return self.get_json(url, headers=hdr, params=self.response_format)
        else:
            return self.get(url, headers=hdr, params=self.response_format)

    def roster(self, team_key, subresource='players', roster_date=None):
        '''
        Gets team resource

        Args:
            team_key (str): id for team
            subresource (str): default 'players'
            roster_date (str): in YYYY-mm-dd format

        Returns:
            dict: parsed json

        '''
        if subresource not in self.roster_subresources:
            raise ValueError('invalid roster subresource')
        if roster_date:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/{}/roster/{};date={}'
            return self.query(url.format(team_key, subresource, roster_date))
        else:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/{}/roster/{}'
            return self.query(url.format(team_key, subresource))

    def team(self, team_key, subresource='metadata'):
        '''
        Gets team resource

        Args:
            team_key (str): id for team
            subresource (str):

        Returns:
            dict: parsed json

        '''
        if subresource not in self.team_subresources:
            raise ValueError('invalid team subresource')
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/{}/{}'
        return self.query(url.format(team_key, subresource))

    def teams(self, league_id=None, team_keys=None, my_team=False, subresource='metadata'):
        '''
        Gets teams collection

        Args:
            league_id (int): id for your league
            team_keys (list): of team keys
            subresource (str): default 'metadata'

        Returns:
            dict: parsed json

        '''
        if subresource not in self.teams_subresources:
            raise ValueError('invalid teams subresource')
        if league_id:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}/teams/{}'
            return self.query(url.format(self._league_key(league_id), subresource))
        elif team_keys:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/teams;team_keys={}/{}'
            return self.query(url.format(','.join(team_keys), subresource))
        elif my_team:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/teams/{}'
            return self.query(url.format(subresource))
        else:
            raise ValueError('need to specify league_id or team_keys or my_team')

    def transaction(self, transaction_key, subresource='metadata'):
        '''
        Gets transaction resource

        Args:
            transaction_key (str): id for transaction
            subresource (str):

        Returns:
            dict: parsed json

        '''
        if subresource not in self.transaction_subresources:
            raise ValueError('invalid transaction subresource')
        url = 'https://fantasysports.yahooapis.com/fantasy/v2/transaction/{}/{}'
        return self.query(url.format(transaction_key, subresource))

    def transactions(self, league_id, subresource='metadata', filters=None):
        '''
        Gets transactions resource

        Args:
            league_id (int): id for league
            subresource (str):
            filters (dict):

        Returns:
            dict: parsed json

        '''
        if subresource not in self.transactions_subresources:
            raise ValueError('invalid transactions subresource')
        elif filters:
            if set(filters.keys()) <= set(self.transactions_filters):
                url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}/transactions;{}'
                return self.query(url.format(self._league_key(league_id), self._filtstr(filters)))
            else:
                raise ValueError('games invalid filters: {}'.format(filters))
        else:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/{}/transactions/{}'
            return self.query(url.format(self._league_key(league_id), subresource))

    def user(self, subresource=None):
        '''
        Gets user resource. Yahoo recommends using users collection instead

        Args:
            subresource (str): default None

        Returns:
            dict:

        '''
        if subresource:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys={}/{}'
            return self.query(url.format(self.game_key, subresource))
        else:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys={}'
            return self.query(url.format(self.game_key))

    def users(self, subresource=None):
        '''
        Gets users collection

        Args:
            subresource (str): default None

        Returns:
            dict

        '''
        if subresource:
            url = 'https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys={}/{}'
            return self.query(url.format(self.game_key, subresource))
        else:
            return self.query('https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1')


class Parser():
    '''
    Parse yahoo fantasy sports API results

    '''
    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._stat_ids = {
          0: 'games_played', 5: 'fgp', 7: 'ftm',
          10: 'tpm', 12: 'pts', 15: 'reb', 16: 'ast',
          17: 'stl', 18: 'blk', 19: 'tov'}

    @staticmethod
    def _strip_ns(content):
        '''
        Strips namespace from xml

        Args:
            content(str):

        Returns:
            str

        '''
        return re.sub(r'\sxmlns="[^"]+"', '', str(content), count=1)

    def _game_stat_categories(self, content):
        '''
        Parses stat_categories from game resource

        Args:
            content (str):

        Returns:
            list: of dict
        '''

    def _stat_name(self, stat_id):
        '''
        Yahoo standings use stat id rather than name

        '''
        return self._stat_ids.get(stat_id)
          
    def game(self, content):
        '''
        Parses game resource

        Args:
            content (str):

        Returns:
            list: of dict

        '''
        root = ET.fromstring(Parser._strip_ns(content))
        return [{child.tag: child.text for child in game} for game in root.iter('game')]

    def league_standings(self, content):
        '''
        Parses league with standings subresource

        Args:
            content(str): XML string
            
        Returns:
            list: of dict
            
        '''
        vals= []
        root = ET.fromstring(Parser._strip_ns(content))
        for team in root.findall(".//standings/teams/team"):
            team_d = {'team_key': team.find('team_key').text,
                      'team_name': team.find('name').text}
            team_standings = team.find('team_standings')
            team_d['rank'] = team_standings.find('rank').text
            team_d['points_for'] = team_standings.find('points_for').text
            for stat in team.find('.//team_stats/stats'):
                stat_id = int(stat.find('stat_id').text)
                stat_name = self._stat_name(stat_id)
                if stat_name:
                    val = stat.find('value').text               
                    team_d[stat_name] = val
            for stat in team.find('.//team_points/stats'):
                stat_id = int(stat.find('stat_id').text)
                stat_name = self._stat_name(stat_id)
                if stat_name:
                    val = stat.find('value').text               
                    team_d[f'{stat_name}_pts'] = val
            vals.append(team_d)
        return vals
        
    def leagues(self, content):
        '''
        Parses leagues collection

        Args:
            content (str): XML

        Returns:
            list: of dict

        '''
        root = ET.fromstring(Parser._strip_ns(content))
        return [{child.tag: child.text for child in league} for league in root.iter('league')]

    def user_leagues(self, content, game_key):
        '''
        Parses user collection with leagues subresource

        Args:
            content(str): XML
            game_key(int): e.g. 385

        Returns:
            list: of dict

        '''
        root = ET.fromstring(Parser._strip_ns(content))
        vals = []
        for node in root.findall(".//game"):
            if node.find('game_key').text == str(game_key):
                for league in node.findall('.//league'):
                   vals.append({child.tag: child.text for
                                child in league}) 
        return vals  

        
        
        
if __name__ == '__main__':
    pass
