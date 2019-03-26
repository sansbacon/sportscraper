"""
fantasylabs.py

Parser and agent for site

Usage:

    from sportscraper.fantasylabs import Agent
    import os

    a = Agent(profile=os.getenv('FIREFOX_PROFILE'))
    model = a.s.model('nba')
    pl = a.p.site_players(model, 'dk')
    print(pl)

"""

import logging
from random import random, randint
from time import sleep

from sportscraper import BrowserScraper
from .dates import today


class BScraper(BrowserScraper):
    """
    Uses browser to access fantasylabs resources

    """

    def model(self, sport, datestr=None, model_id="1950741"):
        """

        Args:
            sport(str): 'nba', etc.
            datestr(str): in '%m_%d_%Y' format

        Returns:
            dict - parsed JSON

        """
        if not datestr:
            datestr = today(fmt="fl")

        if sport == "nba":
            referrer_url = "https://www.fantasylabs.com/nba/player-models/"
            model_url = (
                f"https://www.fantasylabs.com/api/playermodel/2/"
                f"{datestr}/?modelId={model_id}&projOnly=true"
            )
            self.get(referrer_url)
            sleep(randint(1, 3) * random())
            return self.get_json(model_url)
        else:
            raise ValueError("sports other than NBA not implemented yet")


class Parser:
    """
    Parses fantasylabs JSON resources

    """

    def __init__(self):
        """

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def model(self):
        """

        Returns:

        """
        pass

    def site_players(self, model, site="dk", wanted=None):
        """
        Gets all players from single DFS site

        Args:
            model(dict): parsed JSON
            site(str): site name ('fd', 'dk', 'fdr', 'yh'), default DK
            wanted(list): wanted keys from Properties

        Returns:
            list: of dict

        """
        players = model["PlayerModels"]
        if not wanted:
            wanted = [
                "AvgPts",
                "Ceiling",
                "CeilingPct",
                "Floor",
                "FloorPct",
                "InjuryStatus",
                "PlayerId",
                "Player_Name",
                "Position",
                "PositionId",
                "Salary",
                "Score",
                "SourceId",
                "Team",
                "p_own_num",
            ]
        sites = {"fd": 3, "dk": 4, "fdr": 7, "yh": 11}
        site_id = sites.get(site)
        site_players = [
            p["Properties"] for p in players if p["Properties"]["SourceId"] == site_id
        ]
        return [{k: v for k, v in sp.items() if k in wanted} for sp in site_players]


class Agent:
    """
    Combines scraper and parser for common tasks

    """

    def __init__(self, profile, sport):
        """
        Creates Agent object

        Args:
            profile(str): filename of profile
            sport(str): 'nba', 'nfl', etc.

        Returns:
            Agent

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.scraper = BScraper(profile=profile)
        self.parser = Parser()
        self.sport = sport

    def matchups(self, datestr=None):
        """
        Gets matchups from one day

        Args:
            datestr(str): string for date of model

        Returns:
            list: of dict

        """
        pass

    def model(self, datestr=None):
        """
        Gets model from one day

        Args:
            datestr(str): string for date of model

        Returns:
            list: of dict

        """
        pass

    def site_players(self, site="dk", datestr=None):
        """
        Gets player data for one dfs site

        Args:
            site(str): 'dk', 'fd', etc.
            datestr(str): string for date of model

        Returns:
            list: of dict

        """
        model = self.scraper.model(self.sport, datestr)
        return self.parser.site_players(model, site)


if __name__ == "__main__":
    pass
