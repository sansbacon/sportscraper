'''
draftkings.py
classes to scrape draftkings contests, etc.

'''
import logging
from random import random, randint
from time import sleep

from sportscraper import RequestScraper, BrowserScraper


class Scraper(RequestScraper):
    '''

    '''
    def scrape(self):
        '''
        Stub method

        Returns:
            None

        '''
        pass


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

    def contests(self, sport):
        '''
        Gets contests

        Args:
            sport(str): 'NFL', 'NBA', etc.

        Returns:
            str

        '''
        url = f'https://www.draftkings.com/lobby/getcontests?sport={sport}'
        return self.get(url)

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

    def lobby(self):
        '''
        Gets lobby contests

        Args:
            None

        Returns:
            str

        '''
        url = 'https://www.draftkings.com/lobby/'
        return self.get(url)


if __name__ == '__main__':
    pass
