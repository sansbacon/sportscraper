# scraper.py
"""
Scraper classes for use in nfl, nba, etc.

"""

import datetime
import hashlib
import json
import logging
import os
import psutil
import random
import re
import time
from urllib.parse import urlencode

from requests_html import HTMLSession

try:
    from pyvirtualdisplay import Display
except ImportError:
    pass

try:
    from selenium import webdriver
except ImportError:
    pass

try:
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.remote.errorhandler import WebDriverException
    from selenium.common.exceptions import (
        TimeoutException,
        InsecureCertificateException,
    )
except ImportError:
    pass

from .utility import random_string


USER_AGENTS = (
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
    ),
    (
        "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 "
        "(KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"
    ),
    (
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36)"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, "
        "like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    ),
)


class RequestScraper:
    """
    Base class for scraping using requests_html session

    """

    def __init__(self, **kwargs):
        """
        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.urls = []

        # use requests HTML to aid parsing
        # has all same methods as requests.Session
        _s = HTMLSession()
        self.delay = kwargs.get("delay", 2)
        self.expire_hours = kwargs.get("expire_hours", 168)

        # add cookies
        if kwargs.get("cookies"):
            _s.cookies = kwargs["cookies"]
        else:
            import http.cookiejar

            _s.cookies = http.cookiejar.MozillaCookieJar()

        # add headers
        default_headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "accept": "application/json, text/plain, */*",
        }
        _s.headers.update(default_headers)
        if kwargs.get("headers"):
            _s.headers.update(kwargs["headers"])

        # add proxies
        if kwargs.get("proxies"):
            _s.proxies = kwargs["proxies"]

        # add cache
        if not kwargs.get("cache_name"):
            self.cache_name = os.path.join("/tmp", random_string(32))
        elif "/" not in kwargs.get("cache_name", ""):
            self.cache_name = os.path.join("/tmp", kwargs["cache_name"])
        else:
            self.cache_name = kwargs.get("cache_name")

        try:
            from cachecontrol import CacheControlAdapter
            from cachecontrol.heuristics import ExpiresAfter
            from cachecontrol.caches import FileCache

            _s.mount(
                "http://",
                CacheControlAdapter(
                    cache=FileCache(self.cache_name),
                    cache_etags=False,
                    heuristic=ExpiresAfter(hours=self.expire_hours),
                ),
            )
        except ImportError:
            try:
                import requests_cache

                requests_cache.install_cache(self.cache_name)
            except BaseException:
                logging.exception("could not install cache")
        self.session = _s

    @property
    def headers(self):
        """
        Request headers

        """
        return self.session.headers

    @headers.setter
    def headers(self, value):
        """
        Update request headers

        Args:
            value(dict): additional headers

        """
        self.session.headers.update(value)

    def get(
        self, url, params=None, headers=None, encoding="utf-8", return_object=False
    ):
        """
        Args:
            url(str):
            params(dict): url parameters
            headers(dict): header dict
            encoding(str): default utf-8
            include_object(bool):

        Returns:
            str

        """
        if headers:
            self.session.headers.update(headers)

        if params:
            resp = self.session.get(
                url, params={k: params[k] for k in sorted(params)}, headers=self.headers
            )
        else:
            resp = self.session.get(url, headers=self.headers)
        self.urls.append(resp.url)
        resp.raise_for_status()
        if resp.status_code == 304:
            resp = self.session.get(url, headers=self.headers)
        if self.delay:
            time.sleep(self.delay)
        if return_object:
            return resp
        return resp.content.decode(encoding)

    def get_filecache(self, url, savedir="/tmp", encoding="utf-8"):
        """
        Uses file-based caching, helpful for debugging because can look at files

        Args:
            url(str):
            savedir(str):
            encoding(str):

        Returns:
            str

        """
        file_name = os.path.join(
            savedir, "{}.html".format(hashlib.md5(url).hexdigest())
        )
        if os.path.exists(file_name):
            with open(file_name, "rb") as infile:
                content = infile.read()
        else:
            resp = self.session.get(url)
            self.urls.append(resp.url)
            resp.raise_for_status()
            content = resp.content.decode(encoding)
            with open(file_name, "wb") as outfile:
                outfile.write(content)
            if self.delay:
                time.sleep(self.delay)
        return content

    def get_json(self, url, headers=None, payload=None):
        """
        Gets JSON resource and (default) parses into python data structure

        Args:
            url(str):
            payload(dict): query string parameters

        Returns:
            dict

        """
        if headers:
            self.session.headers.update(headers)

        if payload:
            resp = self.session.get(
                url,
                headers=self.headers,
                params={k: payload[k] for k in sorted(payload)},
            )
        else:
            resp = self.session.get(url, headers=self.headers, params=None)
        self.urls.append(resp.url)
        resp.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return resp.json()

    def get_tor(self, url):
        """
        Makes request over TOR network

        """
        try:
            from torrequest import TorRequest

            with TorRequest() as tor_req:
                content = tor_req.get(url)
                self.urls.append(url)
                tor_req.reset_identity()
                return content
        except BaseException:
            logging.exception("could not get over tor %s", url)
            return self.get(url)

    def post(self, url, data, headers=None, params=None):
        """

        Args:
            url (str): url for post
            data (dict): data to post
            headers (dict): HTTP headers
            params (str): key-value URL parameters

        Returns:
            HTTPResponse

        """
        if headers:
            self.session.headers.update(headers)
        resp = self.session.post(url, data, headers=self.headers, params=params)
        self.urls.append(resp.url)
        resp.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return resp


class BrowserScraper:
    """
    Scraper using selenium

    """

    def __init__(self, profile, visible=False, cache_dir=None):
        """
        Scraper using selenium

        Args:
            profile(str): path to firefox profile
            visible(bool): show browser, use virtual display if False
            cache_dir(str): default /tmp

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.urls = []
        self.cachedir = cache_dir

        if not visible:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

        caps = DesiredCapabilities.FIREFOX.copy()
        caps["marionette"] = True
        if profile:
            self.browser = webdriver.Firefox(
                capabilities=caps, firefox_profile=profile, log_path=os.devnull
            )
        else:
            self.browser = webdriver.Firefox(capabilities=caps, log_path=os.devnull)
        self.browser.set_page_load_timeout(30)

    def __del__(self):
        """
        Clean up zombie processes

        """
        procnames = ["Xvfb", "geckodriver"]
        try:
            for proc in psutil.process_iter():
                # check whether the process name matches
                if proc.name() in procnames:
                    proc.kill()
        except:
            pass

    def get(self, url, payload=None):
        """
        Gets page using headless firefox

        Args:
            url: string

        Returns:
            string of HTML
        """
        if payload:
            url = f"{url}?{urlencode(payload)}"
        self.urls.append(url)
        if self.cachedir:
            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
            file_name = os.path.join(self.cachedir, f"{url_hash}.html")
            if os.path.exists(file_name):
                with open(file_name, "rb") as infile:
                    return infile.read()
        try:
            self.browser.get(url)
        except (InsecureCertificateException, BrokenPipeError, TimeoutException):
            time.sleep(1)
            self.browser.get(url)
        return self.browser.page_source

    def get_json(self, url, payload=None):
        """

        Args:
            url:

        Returns:
            dict parsed json
        """
        if payload:
            url = "{}?{}".format(url, urlencode(payload))
        self.urls.append(url)
        if self.cachedir:
            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
            file_name = os.path.join(self.cachedir, f"{url_hash}.html")
            if os.path.exists(file_name):
                with open(file_name, "rb") as infile:
                    return infile.read()
        self.browser.get(url)
        content = self.browser.find_element_by_tag_name("body").text
        return json.loads(content)

    def get_jsvar(self, varname):
        """
        Gets python data structure of javascript variable

        Args:
            varname (str): name of javascript variable

        Returns:
            whatever the type of the javascript variable

        """
        try:
            return self.browser.execute_script("return {};".format(varname))
        except WebDriverException as err:
            logging.exception(err)
            return None

    def requests(self, dump=True):
        """
        Retrieves and dumps request information

        Args:
            dump(bool): print request information

        Returns:
            list

        """
        responses = []
        for request in self.browser.requests:
            if request.response:
                responses.append(request.response)
                if dump:
                    print(
                        request.path,
                        request.response.status_code,
                        request.response.headers["Content-Type"],
                    )
        return responses


class WaybackScraper(RequestScraper):
    """
    Scraper for wayback machine. Subclass of RequestScraper.

    """

    def __init__(self, **kwargs):
        """
        Scraper for waybackmachine API

        """
        RequestScraper.__init__(self, **kwargs)
        self.wburl = "http://archive.org/wayback/available?url={}&timestamp={}"

    @staticmethod
    def convert_format(datestr, site):
        """
        Converts string from one date format to another

        Args:
            datestr(str): date as string
            site(str): 'nfl', 'fl', 'std', etc.

        Returns:
            str

        """
        fmt = WaybackScraper.format_type(datestr)
        newfmt = WaybackScraper.site_format(site)
        if fmt and newfmt:
            try:
                dtobj = datetime.datetime.strptime(datestr, fmt)
                return datetime.datetime.strftime(dtobj, newfmt)
            except BaseException:
                return None
        else:
            return None

    @staticmethod
    def format_type(datestr):
        """
        Uses regular expressions to determine format of datestring

        Args:
            datestr (str): date string in a variety of different formats

        Returns:
            fmt (str): format string for date

        """
        val = None
        if re.match(r"\d{1,2}_\d{1,2}_\d{4}", datestr):
            val = WaybackScraper.site_format("fl")
        elif re.match(r"\d{4}-\d{2}-\d{2}", datestr):
            val = WaybackScraper.site_format("nfl")
        elif re.match(r"\d{1,2}-\d{1,2}-\d{4}", datestr):
            val = WaybackScraper.site_format("std")
        elif re.match(r"\d{1,2}/\d{1,2}/\d{4}", datestr):
            val = WaybackScraper.site_format("odd")
        elif re.match(r"\d{8}", datestr):
            val = WaybackScraper.site_format("db")
        elif re.match(r"\w+ \d+, \d+", datestr):
            val = WaybackScraper.site_format("bdy")
        return val

    @staticmethod
    def site_format(site):
        """
        Stores date formats used by different sites

        Args:
            site(str):

        Returns:
            str

        """
        return {
            "std": "%m-%d-%Y",
            "fl": "%m_%d_%Y",
            "fl2017": "%m-%d-%Y",
            "fl_matchups": "%-m-%-d-%Y",
            "nfl": "%Y-%m-%d",
            "odd": "%m/%d/%Y",
            "db": "%Y%m%d",
            "bdy": "%B %d, %Y",
            "espn_fantasy": "%Y%m%d",
        }.get(site, None)

    @staticmethod
    def strtodate(dstr):
        """
        Converts date formats used by different sites

        Args:
            dstr(dstr): datestring

        Returns:
            datetime.datetime

        """
        fmt = WaybackScraper.format_type(dstr)
        return datetime.datetime.strptime(dstr, fmt)

    @staticmethod
    def subtract_datestr(date1, date2):
        """
        Subtracts d2 from d1

        Args:
            date1(str): '2018-01-01'
            date2(str): '2017-12-12'

        Returns:
            int: number of days between dates

        """
        if isinstance(date1, str):
            delta = WaybackScraper.strtodate(date1) - WaybackScraper.strtodate(date2)
        else:
            delta = date1 - date2
        return delta.days

    @staticmethod
    def today(fmt="nfl"):
        """
        Datestring for today's date

        Args:
            fmt(str): 'nfl'

        Returns:
            str

        """
        fmt = WaybackScraper.site_format(fmt)
        if not fmt:
            raise ValueError("invalid date format")
        return datetime.datetime.strftime(datetime.datetime.today(), fmt)

    def get_wayback(self, url, datestr=None, max_delta=None):
        """
        Gets page from the wayback machine

        Args:
            url: of the site you want, not the wayback machine
            datestr: datestring, if None then get most recent one
            max_delta: int, how many days off can the last page be from the requested date

        Returns:
            content: HTML string

        """
        content = None
        time_stamp = None

        if not datestr:
            datestr = WaybackScraper.today("db")
        else:
            datestr = WaybackScraper.convert_format(datestr, "db")
        resp = self.get_json(self.wburl.format(url, datestr))

        if resp:
            try:
                time_stamp = resp["archived_snapshots"]["closest"]["timestamp"][:8]
                if time_stamp and max_delta:
                    closest_url = resp["archived_snapshots"]["closest"]["url"]
                    diff = WaybackScraper.subtract_datestr(datestr, time_stamp)
                    if abs(diff) <= max_delta:
                        url = resp["archived_snapshots"]["closest"]["url"]
                        content = self.get(url)
                    else:
                        logging.error("page is too old: %s", time_stamp)
                else:
                    closest_url = resp["archived_snapshots"]["closest"]["url"]
                    content = self.get(closest_url)
            except (TypeError, ValueError) as err:
                logging.exception(err)
        else:
            logging.error("url unavailable on wayback machine")

        return content, time_stamp


if __name__ == "__main__":
    pass
