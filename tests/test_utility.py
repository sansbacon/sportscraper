# test_utility.py

import pytest

from sportscraper.utility import *


def test_digits():
    digitstr = 'a123'
    assert '123' == digits(digitstr)


def test_flatten():
    d = {'a': {'b': 1}}
    assert flatten(d) == {'b': 1}


def test_flatten_list():
    l = [[1,2], [3,4]]
    assert flatten_list(l) == [1, 2, 3, 4]


def test_isfloat():
    x = 3
    assert isfloat(x)
    x = 'abc'
    assert not isfloat(x)


def test_isint():
    x = 3.0
    assert not isint(x)
    x = 'abc'
    assert not isint(x)


def test_merge_two():
    d1 = {'a': 1}
    d2 = {'b': 2}
    assert merge_two(d1, d2) == {'a': 1, 'b': 2}


def test_rand_dictitem():
    d1 = {'a': 1, 'b': 2}
    rand_item = rand_dictitem(d1)
    assert isinstance(rand_item[0], str)
    assert isinstance(rand_item[1], int)


def test_random_string():
    string_length = random.randint(10, 32)
    assert string_length == len(random_string(string_length))


def test_sample_dict():
    n = 2
    d1 = {'a': 1, 'b': 2, 'c': 3}
    rand_sample = sample_dict(d1, n)
    assert isinstance(rand_sample, dict)
    assert len(rand_sample) == n


def test_valornone():
    val = 3
    assert valornone(val) == 3
    assert not valornone('')

