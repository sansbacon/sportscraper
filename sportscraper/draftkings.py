'''
draftkings.py

Parser and agent for nba contests

'''
from collections import defaultdict
import csv
from datetime import datetime
import io
import logging
from random import random, randint
import re
from time import sleep

from sportscraper import RequestScraper, BrowserScraper


class Scraper(RequestScraper):
    '''

    '''
    def contests(self, sport=None):
        '''
        Gets dk contests

        Args:
            sport(str): default None

        Returns:
            dict

        '''
        url = 'https://www.draftkings.com/lobby/getcontests'
        if sport:
            params = {'sport': sport}
            return self.get_json(url, params)
        return self.get_json(url)

    def draftables(self, draft_group_id):
        '''
        Gets draftables JSON

        Args:
            draft_group_id(int): draftgroup ID

        Returns:
            dict

        '''
        url = ('https://api.draftkings.com/draftgroups/v1/draftgroups/'
               '{}/draftables?format=json')
        return self.get_json(url.format(draft_group_id))

    def salaries(self, draft_group_id):
        '''
        Gets salaries csv file

        Returns:
            str

        '''
        csv_url = (f'https://www.draftkings.com/lineup/getavailableplayerscsv?'
                   f'draftGroupId={draft_group_id}')
        return self.get(csv_url)


class BScraper(BrowserScraper):
    '''
    Draftkings browser scrper

    '''
    def __init__(self, profile, visible=False, polite=True):
        '''
        Opens selenium scraper

        Args:
            profile(str):  path to browser profile
            visible(bool): default False
            polite(bool): defa

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        BrowserScraper.__init__(self, profile=profile, visible=visible)
        self.polite = polite

    def _polite(self):
        '''
        Adds small random delay

        '''
        if self.polite:
            sleep(random() * randint(1, 5))

    def contests(self, sport=None):
        '''
        Gets dk contests

        Args:
            sport(str): default None

        Returns:
            dict

        '''
        url = 'https://www.draftkings.com/lobby/getcontests'
        if sport:
            url += f'?sport={sport}'
        return self.get_json(url)

    def draftables(self, draft_group_id):
        '''
        Gets draftables JSON

        Args:
            draft_group_id(int): draftgroup ID

        Returns:
            dict

        '''
        url = ('https://api.draftkings.com/draftgroups/v1/draftgroups/'
               '{}/draftables?format=json')
        return self.get_json(url.format(draft_group_id))

    def get(self, url):
        '''
        Overrides parent get, adds polite delay

        Args:
            url(str):

        Returns:
            str

        '''
        content = BrowserScraper.get(self, url)
        self._polite()
        return content

    def get_json(self, url):
        '''
        Overrides parent get_json, adds polite delay

        Args:
            url(str):

        Returns:
            dict: parsed JSON

        '''
        content = BrowserScraper.get_json(self, url)
        self._polite()
        return content

    def live_contests(self):
        '''
        Gets list of contests

        Returns:
            list: of contest dict

        '''

        url = 'https://www.draftkings.com/mycontests'
        return self.get(url)



class Parser():
    '''
    Common draftkings parser

    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.data = {}

    @staticmethod
    def _contest_date(contest_date, fmt='%m-%d-%Y'):
        '''
        Converts contest epoch string to datetime

        Args:
            contest_date(str): epoch string
            fmt(str): datetime format, default '%m-%d-%Y'

        Returns:
            datetime, str

        '''
        datestr = re.findall(r'\d+', contest_date)[0]
        contest_date = datetime.fromtimestamp(float(datestr) / 1000)
        return contest_date, datetime.strftime(contest_date, fmt)

    def contests(self, content):
        '''
        Parses DK contests json (which is embedded in html response)

        Args:
            content(str):

        Returns:
            dict

        '''
        contest_dicts = []
        headers = ['contest_name', 'contest_date', 'contest_slate', 'contest_fee',
                   'contest_id', 'max_entries', 'contest_size', 'prize_pool',
                   'draft_group_id', 'sport_id']
        for contest in content['Contests']:
            contest_date = Parser._contest_date(contest.get('sd'))
            vals = [contest.get('n'), contest_date, contest.get('sdstring'),
                    contest.get('a'), contest.get('id'), contest.get('mec'),
                    contest.get('m'), contest.get('po'), contest.get('dg'), contest.get('s')]
            contest_dicts.append(dict(zip(headers, vals)))
        return contest_dicts

    def draftables(self, content, wanted=None):
        '''
        Parses draftables file

        Args:
            content(dict):
            wanted(list): keys to create dict

        Returns:
            list: of dict

        '''
        if not wanted:
            wanted = ['firstName', 'lastName', 'displayName',
                      'playerId', 'position', 'rosterSlotId',
                      'salary', 'teamAbbreviation']
        self.data['draftables'] = [
            {k: v for k, v in p.items() if k in wanted} for p in content['draftables']]
        return self.data['draftables']

    def salaries(self, content):
        '''
        Parses salaries csv file

        Args:
            content(str):

        Returns:
            list: of dict

        '''
        try:
            handle = io.StringIO(content)
        except:
            handle = io.BytesIO(content)
        self.data['sals'] = []
        for idx, line in enumerate(handle):
            if idx == 0:
                headers = line.split(',')
            else:
                self.data['sals'].append(dict(zip(headers, line.split(','))))
        return self.data['sals']

    def slate_entries(self, file_name):
        '''
        Parses contest download file from dk.com to get all entries

        Args:
            file_name (str): filename

        Returns:
            list: List of dict

        '''
        self.data['slate_entries'] = []
        with open(file_name, 'r') as infile:
            for idx, row in enumerate(csv.reader(infile)):
                if not row[0]:
                    break
                if idx == 0:
                    headers = row[0:12]
                else:
                    self.data['slate_entries'].append(
                        dict(zip(headers, row[0:12])))
        return self.data['slate_entries']

    def slate_players(self, file_name):
        '''
        Parses slate contest file from dk.com to get all players on slate

        Args:
            file_name (str): filename

        Returns:
            list: List of dict

        '''
        self.data['slate_players'] = []
        with open(file_name, 'r') as infile:
            # strange format in the file
            # data does not start until row 8 (index 7)
            for idx, row in enumerate(csv.reader(infile)):
                if idx < 7:
                    continue
                elif idx == 7:
                    headers = row[14:21]
                else:
                    self.data['slate_players'].append(dict(zip(headers, row)))
        return self.data['slate_players']


class Agent():
    '''
    Draftkings agent class

    '''

    def __init__(self, cache_name=None, profile=None):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        if not cache_name and profile:
            raise ValueError('must specify cache_name, profile, or both')
        if cache_name:
            self.scraper = Scraper(cache_name=cache_name)
        if profile:
            self.bscraper = BScraper(profile)
        self.parser = Parser()
        self.data = {}

    def contests(self, sport=None):
        '''
        '''
        return self.parser.contests(self.scraper.contests(sport))

    def dk_player_d(self, sals):
        '''
        Gets dict of players from salary json

        Args:
            sals(defaultdict): dict with list values

        Returns:
            dict: key is integer, value is string

        '''
        if not self.data.get('dk_player_d'):
            players = {}
            for val in sals.values():
                for item in val:
                    if isinstance(item, dict):
                        players[item.get('playerId')] = item.get('displayName')
            self.data['dk_player_d'] = players
        return self.data['dk_player_d']

    def draftables(self, draft_group_id):
        '''
        Gets draftables for specific group

        Args:
            draft_group_id(int):

        Returns:
            dict

        '''
        return self.parser.draftables(self.scraper.draftables(draft_group_id))

    def salaries(self, draft_group_id):
        '''
        Gets salaries for specific group

        Args:
            draft_group_id(int):

        Returns:
            list: of dict

        '''
        return self.parser.salaries(self.scraper.salaries(draft_group_id))


if __name__ == '__main__':
    pass
