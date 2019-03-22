# test_dates.py

import datetime
import pytest
import random

from sportscraper.dates import *


def test_convert_format():
    datestr = '09-01-2018'
    site = 'nfl'
    assert convert_format(datestr, site) == '2018-09-01'


def test_date_list():
    dl = date_list('10_09_2018', '10_05_2018')
    assert isinstance(dl, list)
    assert isinstance(dl[0], datetime.datetime)
    assert len(dl) == 5
    assert datetime.datetime(2018, 10, 5) == dl[-1]


def test_datetostr():
    dt = datetime.datetime(2018, 10, 5)
    dtstr = datetostr(dt, 'nfl')
    assert dtstr == '2018-10-05'


def test_format_type():
    datestr = '2018-01-01'
    assert format_type(datestr) == '%Y-%m-%d'
    datestr = '01_01_2018'
    assert format_type(datestr) == '%m_%d_%Y'
    datestr = '01/01/2018'
    assert format_type(datestr) == '%m/%d/%Y'


def test_site_format():
    assert site_format('nfl') == '%Y-%m-%d'
    assert site_format('fl') == '%m_%d_%Y'
    assert site_format('odd') == '%m/%d/%Y'


def test_strtodate():
    for datestr in ['10_05_2018', '2018-10-05', '10-05-2018', '10/05/2018']:
        assert datetime.datetime(2018, 10, 5) == strtodate(datestr)


def test_subtract_datestr():
    d1 = '2018-01-01'
    d2 = '2017-12-30'
    assert subtract_datestr(d1, d2) == 2


def test_today():
    fmt = 'nfl'
    assert today(fmt) == datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')


def test_yesterday():
    fmt = 'nfl'
    assert yesterday(fmt) == datetime.datetime.strftime(
        datetime.datetime.today() - datetime.timedelta(1), '%Y-%m-%d')


def test_yesterday_x():
    interval = 3
    fmt = 'nfl'
    assert yesterday_x(interval, fmt) == datetime.datetime.strftime(
        datetime.datetime.today() - datetime.timedelta(interval), '%Y-%m-%d')
