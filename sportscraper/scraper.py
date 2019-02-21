# scraper.py

import hashlib
import json
import logging
import os
import re
import time
from urllib.parse import urlparse, urlencode

from requests_html import HTMLSession


class RequestScraper():

    def __init__(self, **kwargs):
        '''
        Base class for common scraping tasks

        Args:

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.urls = []

        # use requests HTML to aid parsing
        # has all same methods as requests.Session
        _s = HTMLSession()

        # delay/expire
        if kwargs.get('delay'):
            self.delay = kwargs['delay']
        else:
            self.delay = 2

        if kwargs.get('expire_hours'):
            self.expire_hours = kwargs['expire_hours']
        else:
            self.expire_hours = 168

        # add cookies
        if kwargs.get('cookies'):
            _s.cookies = kwargs['cookies']
        else:
            try:
                import cookielib
                _s.cookies = cookielib.MozillaCookieJar()
            except (NameError, ImportError):
                import http.cookiejar
                _s.cookies = http.cookiejar.MozillaCookieJar()
                
        # add headers
        if kwargs.get('headers'):
            _s.headers = kwargs['headers']
        else:
            ua = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')
            _s.headers = {'User-Agent': ua}

        # add proxies
        if kwargs.get('proxies'):
            _s.proxies = kwargs['proxies']

        # add cache
        if not '/' in kwargs.get('cache_name', ''):
            self.cache_name = os.path.join('/tmp', kwargs['cache_name'])
        try:
            from cachecontrol import CacheControlAdapter
            from cachecontrol.heuristics import ExpiresAfter
            from cachecontrol.caches import FileCache
            _s.mount('http://', CacheControlAdapter(cache=FileCache(self.cache_name), 
                                    cache_etags = False,
                                    heuristic=ExpiresAfter(hours=self.expire_hours)))
        except ImportError as e:
            try:
                import requests_cache
                requests_cache.install_cache(self.cache_name)
            except:
                logging.exception('could not install cache')
        self.s = _s

    @property
    def headers(self):
        return self.s.headers

    @headers.setter
    def headers(self, value):
        self.s.headers.update(value)

    def get(self, url, payload=None, encoding='utf-8', return_object=False):
        '''
        Args:
            url(str):
            payload(dict):
            encoding(str):
            include_object(bool):

        Returns:
            str

        '''
        if payload:
            r = self.s.get(url, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url)
        self.urls.append(r.url)
        r.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        if return_object:
            return r
        else:
            return r.content.decode(encoding)

    def get_filecache(self, url, savedir='/tmp', encoding='utf-8'):
        '''
        Uses file-based caching, helpful for debugging because can look at files

        Args:
            url(str):
            savedir(str):
            encoding(str):

        Returns:
            str

        '''
        fn = os.path.join(savedir, '{}.html'.format(hashlib.md5(url).hexdigest()))
        if os.path.exists(fn):
            with open(fn, 'rb') as infile:
                content = infile.read()
        else:
            r = self.s.get(url)
            self.urls.append(r.url)
            r.raise_for_status()
            content = r.content.decode(encoding)
            with open(fn, 'wb') as outfile:
                outfile.write(content)
            if self.delay:
                time.sleep(self.delay)
        return content

    def get_json(self, url, payload=None):
        '''
        Gets JSON resource and (default) parses into python data structure

        Args:
            url(str):
            payload(dict): query string parameters

        Returns:
            dict

        '''
        if payload:
            r = self.s.get(url, headers=self.headers, params={k:payload[k] for k in sorted(payload)})
        else:
            r = self.s.get(url, headers=self.headers, params=None)
        self.urls.append(r.url)
        r.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return r.json()

    def get_tor(self, url):
        '''
        Makes request over TOR network

        '''
        try:
            from torrequest import TorRequest
            with TorRequest() as tr:
                content = tr.get(url)
                tr.reset_identity()
                return content
        except:
            logging.exception('could not get %s' % url)
            return None

    def post(self, url, payload):
        '''

        Args:
            url (str): url for post
            payload (dict): data to post

        Returns:
            HTTPResponse

        '''
        r = self.s.post(url, headers=self.headers, params=payload)
        self.urls.append(r.url)
        r.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return r


class BrowserScraper():
    '''
    
    '''

    def __init__(self, profile=None, visible=False, cache_dir=None):
        '''
        Scraper using selenium

        Args:
            profile: string, path to firefox profile, e.g. $HOME/.mozilla/firefox/6h98gbaj.default'
        '''
        try:
            from pyvirtualdisplay import Display
        except ImportError:
            pass
        try:
            from seleniumwire import webdriver
        except ImportError:
            from selenium import webdriver
        try:
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            from selenium.webdriver.remote.errorhandler import WebDriverException
            from selenium.common.exceptions import TimeoutException
        except ImportError:
            pass

        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.urls = []
        self.cache_dir = cache_dir

        if not visible:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        caps = DesiredCapabilities.FIREFOX.copy()
        caps['marionette'] = True
        firefox_profile = webdriver.FirefoxProfile(profile)
        if profile:
            self.browser = webdriver.Firefox(capabilities=caps,
                             firefox_profile=firefox_profile,
                             log_path=os.devnull)
        else:
            self.browser = webdriver.Firefox(capabilities=caps, 
                                             log_path=os.devnull)
        self.browser.set_page_load_timeout(15)

    def get(self, url, payload=None):
        '''
        Gets page using headless firefox

        Args:
            url: string

        Returns:
            string of HTML
        '''
        if payload:
            url = '{}?{}'.format(url, urlencode(payload))
        self.urls.append(url)
        if self.cache_dir:
            fn = os.path.join(self.savedir, '{}.html'.format(hashlib.md5(url).hexdigest()))
            if os.path.exists(fn):
                with open(fn, 'rb') as infile:
                    return infile.read()
        try:
            self.browser.get(url)
        except (BrokenPipeError, TimeoutException):
            time.sleep(1)
            self.browser.get(url)
        return self.browser.page_source

    def get_json(self, url, payload=None):
        '''

        Args:
            url:

        Returns:
            dict parsed json
        '''
        if payload:
            url = '{}?{}'.format(url, urlencode(payload))
        self.urls.append(url)
        if self.cache_dir:
            fn = os.path.join(self.savedir, '{}.html'.format(hashlib.md5(url).hexdigest()))
            if os.path.exists(fn):
                with open(fn, 'rb') as infile:
                    return infile.read()
        self.browser.get(url)
        content = self.browser.find_element_by_tag_name('body').text
        return json.loads(content)

    def get_jsvar(self, varname):
        '''
        Gets python data structure of javascript variable

        Args:
            varname (str): name of javascript variable

        Returns:
            whatever the type of the javascript variable

        '''
        try:
            return self.browser.execute_script('return {};'.format(varname))
        except WebDriverException as e:
            logging.exception(e)
            return None

    def requests(self, dump=True):
        '''
        Retrieves and dumps request information
        
        Args:
            dump(bool): print request information
            
        Returns:
            list
            
        '''
        responses = []
        for request in self.browser.requests:
            if request.response:
                responses.append(request.response)
                if dump:
                    print(request.path, 
                          request.response.status_code, 
                          request.response.headers['Content-Type'])
        return responses


class WaybackScraper(FootballScraper):
    '''
    
    '''
    def __init__(self, **kwargs):
        '''
        Scraper for waybackmachine API

        Args:
            headers: dictionary of HTTP headers
            cookies: cookie object, such as browsercookie.firefox()
            cache_name: str 'nbacomscraper'
            expire_hours: how long to cache requests
            as_string: return as raw string rather than json parsed into python data structure

        '''
        RequestScraper.__init__(self, **kwargs)
        self.wburl = 'http://archive.org/wayback/available?url={}&timestamp={}'

    @classmethod
    def convert_format(datestr, site):
    '''
    Converts string from one date format to another

    Args:
        datestr(str): date as string
        site(str): 'nfl', 'fl', 'std', etc.

    Returns:
        str

    '''
    fmt = format_type(datestr)
    newfmt = site_format(site)
    if fmt and newfmt:
        try:
            dtobj = datetime.datetime.strptime(datestr, fmt)
            return datetime.datetime.strftime(dtobj, newfmt)
        except BaseException:
            return None
    else:
        return None

    @classmethod
    def format_type(datestr):
        '''
        Uses regular expressions to determine format of datestring

        Args:
            datestr (str): date string in a variety of different formats

        Returns:
            fmt (str): format string for date

        '''
        val = None
        if re.match(r'\d{1,2}_\d{1,2}_\d{4}', datestr):
            val = site_format('fl')
        elif re.match(r'\d{4}-\d{2}-\d{2}', datestr):
            val = site_format('nfl')
        elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', datestr):
            val = site_format('std')
        elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', datestr):
            val = site_format('odd')
        elif re.match(r'\d{8}', datestr):
            val = site_format('db')
        elif re.match(r'\w+ \d+, \d+', datestr):
            val = site_format('bdy')
        return val

    @classmethod
    def site_format(site):
        '''
        Stores date formats used by different sites

        Args:
            site(str):

        Returns:
            str

        '''
        return {
            'std': '%m-%d-%Y',
            'fl': '%m_%d_%Y',
            'fl2017': '%m-%d-%Y',
            'fl_matchups': '%-m-%-d-%Y',
            'nfl': '%Y-%m-%d',
            'odd': '%m/%d/%Y',
            'db': '%Y%m%d',
            'bdy': '%B %d, %Y',
            'espn_fantasy': '%Y%m%d'
        }.get(site, None)

    @classmethod
    def strtodate(dstr):
        '''
        Converts date formats used by different sites

        Args:
            dstr(dstr): datestring

        Returns:
            datetime.datetime

        '''
        return datetime.datetime.strptime(dstr, format_type(dstr))

    @classmethod
    def subtract_datestr(date1, date2):
        '''
        Subtracts d2 from d1

        Args:
            date1(str): '2018-01-01'
            date2(str): '2017-12-12'

        Returns:
            int: number of days between dates

        '''
        if isinstance(date1, basestring):
            delta = strtodate(date1) - strtodate(date2)
        else:
            delta = date1 - date2
        return delta.days

    @classmethod
    def today(fmt='nfl'):
        '''
        Datestring for today's date

        Args:
            fmt(str): 'nfl'

        Returns:
            str

        '''
        fmt = site_format(fmt)
        if not fmt:
            raise ValueError('invalid date format')
        return datetime.datetime.strftime(datetime.datetime.today(), fmt)
  
    def get_wayback(self, url, d=None, max_delta=None):
        '''
        Gets page from the wayback machine
        Args:
            url: of the site you want, not the wayback machine
            d: datestring, if None then get most recent one
            max_delta: int, how many days off can the last page be from the requested date
        Returns:
            content: HTML string
        '''
        content = None
        ts = None

        if not d:
            d = today('db')
        else:
            d = convert_format(d, 'db')
        resp = self.get_json(self.wburl.format(url, d))

        if resp:
            try:
                ts = resp['archived_snapshots']['closest']['timestamp'][:8]
                if ts and max_delta:
                    closest_url = resp['archived_snapshots']['closest']['url']
                    if abs(subtract_datestr(d, ts)) <= max_delta:
                        content = self.get(resp['archived_snapshots']['closest']['url'])
                    else:
                        logging.error('page is too old: {}'.format(ts))
                else:
                    closest_url = resp['archived_snapshots']['closest']['url']
                    content = self.get(closest_url)

            except Exception as e:
                logging.exception(e)
        else:
            logging.error('url unavailable on wayback machine')

        return content, ts


if __name__ == "__main__":
    pass

