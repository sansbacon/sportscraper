'''
draft.py

classes for DRAFT.com

'''
import csv
import json
import logging
import os

from sportscraper import RequestScraper


class Scraper(RequestScraper):
    '''

    '''
    def __init__(self, **kwargs):
        '''

        Args:

            **kwargs:

        '''

        headers = {
          'Accept': 'application/json, text/javascript, */*; q=0.01',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
          'Connection': 'keep-alive',
          'DNT': '1',
          'Origin': 'https://draft.com',
          'Referer': 'https://draft.com/upcoming',
          'X-Build-Number': '0',
          'X-Client-Sha': os.getenv('DRAFT_SHA'),
          'X-Client-Type': 'web',
          'X-User-Auth-Id': os.getenv('DRAFT_AUTH'),
          'X-User-Token': os.getenv('DRAFT_TOKEN')}
        super().__init__(headers=headers, **kwargs)

    @staticmethod
    def _csv_to_dict(file_name):
        '''
        Takes csv filename and returns dicts

        Arguments:
            file_name(str): name of file to read/parse

        Returns:
            list: of dicts

        '''
        try:
            with open(file_name, 'r') as infile:
                return [{k: v for k, v in row.items()} for row in
                        csv.DictReader(infile, skipinitialspace=True, delimiter=',')]
        except:
            return None

    @staticmethod
    def _json_file(file_name):
        '''
        Opens JSON file from disk

        Args:
            file_name:

        Returns:
            dict: JSON parsed into dict

        '''
        try:
            with open(file_name, 'r') as infile:
                return json.load(infile)
        except:
            return None

    def adp(self, start_date, end_date, season_year,
            participants='', entry_cost=''):
        '''
        Scrapes ADP dashboard

        Args:
            start_date:
            end_date:
            season_year:
            participants:
            entry_cost:

        Returns:
            dict

        '''
        url = 'https://api.playdraft.com/feeds/v2/sports/nfl//season/adp'

        adp_headers = {
            'origin': 'https://draft.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': ('Mozilla/5.0 (X11; Linux x86_64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.99'),
            'accept': '*/*',
            'referer': 'https://draft.com/adp/',
            'authority': 'api.playdraft.com',
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
            'year': season_year,
            'participants': participants,
            'entry_cost': entry_cost,
            'token': 'b44b7f89026d55cce8df379cbfc2b9e3',
        }

        headers = self.headers
        self.session.headers.update(adp_headers)
        content = self.get(url, params=params)
        self.headers = headers
        return content

    def bestball_ownership(self, file_name=None, window_cluster_id=None):
        '''
        Ownership data for one window cluster

        Args:
            file_name(str):
            window_cluster_id(int):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = Parser._json_file(file_name)
        if not content:
            url = (f'https://api.playdraft.com/v1/window_clusters/{window_cluster_id}/'
                  f'ownerships?tournament=false')
            content = self.get_json(url)
        return content

    def bestball_ownership_csv(self, file_name=None,
                               window_cluster_id=None, sport=None):
        '''
        Ownership data for one window cluster. Only file method works.

        Args:
            file_name(str):
            window_cluster_id(int):
            sport(str):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = Parser._csv_to_dict(file_name)
        if not content:
            url = f'https://draft.com/bbo-csv/{window_cluster_id}/all/{sport}/standard'
            content = self.get(url)
        return content

    def clustered_complete_contests(self, file_name=None):
        '''

        Args:
            file_name (str):

        Returns:
            dict

        '''
        contests = None
        if file_name:
            contests = self._json_file(file_name)
        if not contests:
            url = 'https://api.playdraft.com/v1/clustered_complete_contests'
            contests = self.get_json(url=url)
        return contests

    def clustered_results(self, file_name=None, user_id=None):
        '''
        Clustered results

        Args:
            file_name(str):
            user_id(str):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = self._json_file(file_name)
        if not content:
            url = f'https://api.playdraft.com/v1/users/{user_id}/clustered_results'
            content = self.get_json(url=url)
        return content

    def complete_contests(self, file_name=None, window_cluster_id=None):
        '''
        Complete contests for one window cluster

        Args:
            file_name(str):
            window_cluster_id(int):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = self._json_file(file_name)
        if not content:
            url = (f'https://api.playdraft.com/v2/window_clusters/'
                   f'{window_cluster_id}/complete_contests')
            content = self.get_json(url=url)
        return content

    def contest_results(self, file_name=None, contest_id=None):
        '''
        Complete results for one contest

        Args:
            file_name(str):
            contest_id(str):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = self._json_file(file_name)
        if not content:
            url = f'https://api.playdraft.com/v2/series_contests/{contest_id}'
            content = self.get_json(url=url)
        return content

    def draft(self, league_id=None, file_name=None):
        '''

        Args:
            league_id (str):
            file_name (str):

        Returns:
            dict

        '''
        if file_name:
            return self._json_file(file_name)
        elif league_id:
            url = 'https://api.playdraft.com/v3/drafts/{}'
            return self.get_json(url=url.format(league_id))
        else:
            return ValueError('must specify league_id or file_name')

    def player_pool(self, pool_id=None, file_name=None):
        '''

        Args:
            pool_id (int):
            file_name (dict):

        Returns:
            dict

        '''
        if file_name:
            return self._json_file(file_name)
        elif pool_id:
            url = 'https://api.playdraft.com/v5/player_pool/{}'
            return self.get_json(url.format(pool_id))
        else:
            return ValueError('must specify pool_id or fn')

    def window_cluster_results(self, file_name=None, window_cluster_id=None):
        '''
        Results for one window cluster

        Args:
            file_name(str):
            window_cluster_id(int):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = self._json_file(file_name)
        if not content:
            url = f'https://api.playdraft.com/v3/window_clusters/{window_cluster_id}/results'
            content = self.get_json(url)
        return content


class Parser():

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.data = {}
        self._sport_ids = {1: 'nfl', 2: 'nba'}
        self._team_ids = {
            1: {1: 'BUF', 2: 'MIA', 3: 'NYJ', 4: 'NE',
                5: 'CIN', 6: 'CLE', 7: 'BAL', 8: 'PIT',
                9: 'IND', 10: 'JAC', 11: 'HOU', 12: 'TEN',
                13: 'DEN', 14: 'LAC', 15: 'KC', 16: 'OAK',
                17: 'DAL', 18: 'PHI', 19: 'NYG', 20: 'WAS',
                21: 'CHI', 22: 'DET', 23: 'GB', 24: 'MIN',
                25: 'TB', 26: 'ATL', 27: 'CAR', 28: 'NO',
                29: 'SF', 30: 'ARI', 31: 'LA', 32: 'SEA'},
            2: {}
        }

    @staticmethod
    def _contest_result(contest):
        '''
        Parses DRAFT.com contest result

        Args:
            contest(dict):

        Returns:
            dict

        '''
        contest_type = contest['contest_type']
        draft_rosters = contest['draft_rosters'][0]
        contest_dict = {}
        for k in ['id', 'participants', 'entry_cost', 'prize']:
            contest_dict[k] = contest[k]
        for k in ['seconds_per_pick', 'seconds_per_bid', 'salary_cap_amount']:
            contest_dict[k] = contest_type[k]
        for k in ['user_id', 'pick_order', 'points', 'rank', 'winnings']:
            contest_dict[k] = draft_rosters[k]
        return contest_dict

    @staticmethod
    def _combine_bookings_players(bookings, players):
        '''
        Combines players and bookings

        Args:
            bookings (list): of dict
            players (list): of dict

        Returns:
            list: of dict

        '''
        merged = []

        # go through bookings first
        # create bookings dict with player_id: player_dict
        b_wanted = ['id', 'player_id', 'booking_id', 'adp', 'position_id', 'projected_points']
        bookingsd = {}
        for b in bookings:
            pid = b['player_id']
            bd = {k: v for k, v in b.items() if k in b_wanted}
            bd['booking_id'] = bd.pop('id')
            bookingsd[pid] = bd

        # now try to match up with players
        p_wanted = ['first_name', 'last_name', 'team_id', 'injury_status']
        for p in players:
            match = bookingsd.get(p['id'])
            if match:
                merged.append(Parser._merge_two(match, {k: v for k, v in p.items()
                                                if k in p_wanted}))
        return merged

    @staticmethod
    def _merge_two(d1, d2):
        '''

        Args:
            d1:
            d2:

        Returns:

        '''
        context = d1.copy()
        context.update(d2)
        return context

    def _teams(self, teams):
        '''
        Creates list teams and teamsd (id: team)

        Args:
            teams (list):

        Returns:
            tuple

        '''
        twanted = ['abbr', 'city', 'id', 'nickname']
        self.teams = [{k: v for k, v in t.items() if k in twanted} for t in teams]
        self.teamsd = {t['id']: t['abbr'] for t in self.teams}
        return (self.teams, self.teamsd)

    def adp(self, content):
        '''

        Args:
            content:

        Returns:
            list: of dict (name, team, adp, sportradar_id,
                           min_pick, max_pick, position)

        '''
        self.data['adp'] = content['average_draft_positions']
        return self.data['adp']

    def bestball_ownership(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        self.data['ownership_data'] = []
        bookings = content['bookings']
        players = content['players']
        positions = content['positions']
        total_drafts = content['total_drafts']
        posd = {int(pos['id']): pos['name'] for pos in positions}

        combined = Parser._combine_bookings_players(bookings, players)
        bookings_d = {combine['booking_id']:combine for combine in combined}

        for owned_player in content['ownerships']:
            player_d = Parser._merge_two(owned_player, bookings_d.get(owned_player['booking_id']))
            player_d['position'] = posd.get(player_d['position_id'])
            player_d['total_drafts'] = float(total_drafts)
            player_d['ownership_pct'] = round(player_d['total'] / player_d['total_drafts'], 3)
            self.data['ownership_data'].append(player_d)
        return self.data['ownership_data']

    def clustered_complete_contests(self, content):
        '''
        Parses clustered complete contests

        Args:
            content(dict):

        Returns:
            list: of int

        '''
        return [window['id'] for window in content['window_clusters']]

    def clustered_results(self, content):
        '''
        Parses clustered results

        Args:
            content(dict):

        Returns:
            list: of dict

        '''
        window_cluster_dicts = []
        wanted = ['id', 'sport_id', 'results']
        for window_cluster in content['window_clusters']:
            wc_dict = {k: v for k, v in window_cluster.items() if k in wanted}
            wc_dict['sport'] = self.sport_ids(wc_dict['sport_id'])
            if 'Regular Season' in window_cluster['header_text']:
                wc_dict['contest_type'] = 'bestball'
            elif 'Drafts' in window_cluster['header_text']:
                wc_dict['contest_type'] = 'snake'
            elif 'Auction' in window_cluster['header_text']:
                wc_dict['contest_type'] = 'auction'
            window_cluster_dicts.append(wc_dict)
        return window_cluster_dicts

    def complete_contests(self, content):
        '''
        Parses complete_contests resource. Does not get list of draft picks.

        Args:
            content (dict): complete contests json file

        Returns:
            list: of contest dict

        '''
        return [{'prize': float(dr['prize']), 'player_pool_id': dr['time_window_id'],
                 'entry_cost': float(dr['entry_cost']), 'draft_time': dr['draft_time'],
                 'participants': dr['max_participants'], 'league_id': dr['id'],
                 'league_json': dr} for dr in content['drafts']]

    def contest_results(self, content):
        '''
        Parses detailed results from one contest

        Args:
            content(dict): parsed JSON

        Returns:
            list: of dict

        '''
        # root element and desired keys
        contest = content['series_contest']
        contest_wanted = ['id', 'participants', 'sport_id', 'entry_cost', 'prize']
        contest_metadata = {k:v for k,v in contest.items()
                            if k in contest_wanted}
        for k in ['seconds_per_pick', 'salary_cap_amount', 'seconds_per_bid', 'style']:
            contest_metadata[k] = contest['contest_type'][k]

        # list of dict
        teams_wanted = ['id', 'pick_order', 'winnings', 'rank', 'points', 'user_id']
        teams = [{k:v for k,v in team.items() if k in teams_wanted}
                 for team in contest['draft_rosters']]

        # list of dict
        weekly_results = []
        for week in contest['draft_sections']:
            for k,v in week['roster_points'].items():
                team_week_dict = {'week_id': week['section_id'],
                    'team_id': k, 'week_points': float(v)}
                weekly_results.append(team_week_dict)

        # list of dict
        users_wanted = ['id', 'username', 'experienced', 'skill_level']
        users = [{k: v for k, v in user.items() if k in users_wanted}
                 for user in contest['users']]

        return contest_metadata, teams, users, weekly_results

    def draft_picks(self, draft):
        '''
        Parses single draft resource into picks

        Args:
            draft (dict):

        Returns:
            list: of dict

        '''
        picks = []
        if draft.get('draft'):
            draft = draft['draft']
        teams, teamsd = self._teams(draft['teams'])
        posd = {int(pos['id']): pos['name'] for pos in draft['positions']}

        # players
        players = []
        for p in self._combine_bookings_players(draft['bookings'], draft['players']):
            tid = p.get('team_id')
            if tid:
                p['team_abbr'] = teamsd.get(tid, 'FA')
            else:
                p['team_abbr'] = 'FA'

            p['position'] = posd.get(p['position_id'])
            players.append(p)

        # bookings_xref
        player_bookings_d = {p['booking_id']: p for p in players}

        # picks
        rosters = draft['draft_rosters']
        pkwanted = ['booking_id', 'id', 'draft_roster_id', 'pick_number', 'slot_id']
        for t in rosters:
            for pick in [{k: v for k, v in pk.items() if k in pkwanted} for pk in t['picks']]:
                pick['user_id'] = t['user_id']
                pick['league_id'] = draft['id']

                # add player data
                match = player_bookings_d.get(pick['booking_id'])
                if match:
                    pickc = Parser._merge_two(pick, match)
                else:
                    logging.info('no bookings match for {}'.format(pickc))
                picks.append(pickc)
        return picks

    def draft_users(self, draft):
        '''
        Parses single draft resource into users and user_league

        Args:
            draft (dict):

        Returns:
            tuple: (list of dict, list of dict)

        '''
        if draft.get('draft'):
            draft = draft['draft']
        uwanted = ['experienced', 'id', 'skill_level', 'username']
        users = [{k: v for k, v in user.items() if k in uwanted}
                 for user in draft['users']]
        league_users = [{'league_id': draft['id'],
                         'user_id': dr['user_id'],
                         'pick_order': dr['pick_order']}
                        for dr in draft['draft_rosters']]
        return users, league_users

    def player_pool(self, pp, pool_date):
        '''
        Parses player_pool resource

        Args:
            pp (dict): player_pool resource - parsed JSON into dict
            pool_date (str): e.g. '2018-04-10'

        Returns:
            list: of dict

        '''
        # no need for top-level 'player_pool' key
        if pp.get('player_pool'):
            pp = pp['player_pool']

        # unique identifier for player pool
        player_pool_id = pp['id']
        teams, teamsd = self._teams(pp['teams'])
        posd = {int(pos['id']): pos['name'] for pos in pp['positions']}

        # loop through booking + player and add fields
        players = []
        ppwanted = ['adp', 'first_name', 'last_name', 'player_id', 'pool_date', 'booking_id',
                    'season_year', 'player_pool_id', 'position', 'team', 'projected_points']
        for pl in self._combine_bookings_players(pp['bookings'], pp['players']):
            pl['player_pool_id'] = player_pool_id
            pl['position'] = posd.get(pl['position_id'])
            pl['team'] = teamsd.get(pl['team_id'], 'FA')
            pl['pool_date'] = pool_date
            pl['season_year'] = int(pool_date[0:4])
            players.append({k: v for k, v in pl.items() if k in ppwanted})
        return players

    def sport_ids(self, sport_id):
        '''
        Gets sport name for sport id

        Args:
            sport_id(int): 1, 2, etc.

        Returns:
            str

        '''
        return self._sport_ids.get(sport_id)

    def team_ids(self, sport_id, team_id):
        '''
        Gets team name for team id

        Args:
            sport_id(int): 1, 2, etc.
            team_id(int): 1, 2, etc.

        Returns:
            str

        '''
        return self._team_ids.get(sport_id, {}).get(team_id)

    def window_cluster_results(self, content):
        '''
        Gets results for one window cluster. Less granular than contest results.

        Args:
            content(dict): parsed JSON

        Returns:
            list: of dict

        '''
        contests = content['series_contests']
        return [Parser._contest_result(contest) for contest in contests]


if __name__ == '__main__':
    pass
