'''
draft.py

classes for DRAFT.com

'''
import json
import logging

from sportscraper import RequestScraper


class Scraper(RequestScraper):
    '''

    '''
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

    def complete_contests(self, file_name=None):
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
            url = 'https://api.playdraft.com/v1/window_clusters/2015/complete_contests'
            contests = self.get_json(url=url)
        return contests

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
            url = 'https://api.playdraft.com/v4/player_pool/{}'
            return self.get_json(url.format(pool_id))
        else:
            return ValueError('must specify pool_id or fn')

    def results(self, file_name=None):
        '''

        Args:
            file_name (dict):

        Returns:
            dict

        '''
        content = None
        if file_name:
            content = self._json_file(file_name)
        if not content:
            url = 'https://api.playdraft.com/v3/window_clusters/2015/results'
            content = self.get_json(url)
        return content


class Parser():

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

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
            list: of dict (name, team, adp, sportradar_id, min_pick, max_pick, position)

        '''
        return content['average_draft_positions']

    def complete_contests(self, cc, season_year):
        '''
        Parses complete_contests resource. Does not get list of draft picks.

        Args:
            cc (dict): complete contests json file
            season_year (int): 2018, etc.

        Returns:
            list: of contest dict

        '''
        return [{'prize': float(dr['prize']), 'player_pool_id': dr['time_window_id'],
                 'entry_cost': float(dr['entry_cost']),
                 'draft_time': dr['draft_time'],
                 'participants': dr['max_participants'],
                 'league_id': dr['id'], 'season_year': season_year,
                 'league_json': dr} for dr in cc['drafts']]

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

    def results(self, content):
        '''

        Args:
            content(dict): parsed JSON

        Returns:
            list: of dict

        '''
        contests = content['series_contests']
        return [Parser._contest_result(contest) for contest in contests]


if __name__ == '__main__':
    pass
