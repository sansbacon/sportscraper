'''
utility.py

Utility functions for sportscraper library

'''

import collections
import csv
import json
import logging
import os
import random
from urllib.parse import urlsplit, parse_qs, urlencode, quote


logger = logging.getLogger(__name__)


def csv_to_dict(filename):
    '''
    Takes csv filename and returns dicts

    Arguments:
        filename (str): name of file to read/parse

    Returns:
        list: List of dicts

    '''
    with open(filename, 'r') as infile:
        for row in csv.DictReader(infile, skipinitialspace=True, delimiter=','):
            yield {k: v for k, v in row.items()}


def digits(s):
    '''
    Removes non-numeric characters from a string

    Args:
        s (str): string with non-numeric characters

    Returns:
        str

    '''
    return ''.join(ch for ch in s if ch.isdigit())


def flatten(d):
    '''
    Flattens nested dict into single dict

    Args:
        d (dict): The original dict

    Returns:
        dict: nested dict flattened into dict

    '''
    items = []
    for k, v in d.items():
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v).items())
        else:
            items.append((k, v))
    return dict(items)


def flatten_list(l):
    '''
    Flattens list of lists into list

    Args:
        l (list): original list of lists

    Returns:
        list

    '''
    try:
        return [item for sublist in l for item in sublist]
    except TypeError:
        return l


def isfloat(x):
    '''
    Tests if conversion to float succeeds

    Args:
        x: value to test

    Returns:
        boolean: True if can convert to float, False if cannot.

    '''
    try:
        float_x = float(x)
        return True
    except ValueError:
        return False


def isint(x):
    '''
    Tests if value is integer

    Args:
        x: value to test

    Returns:
        boolean: True if int, False if not.

    '''
    try:
        a = float(x)
        b = int(a)
        return a == b
    except ValueError:
        return False


def json_to_dict(json_fname):
    '''
    Takes json file and returns data structure

    Args:
        json_fname (str): name of file to read/parse

    Returns:
        dict: Parsed json into dict

    '''
    if os.path.exists(json_fname):
        with open(json_fname, 'r') as infile:
            return json.load(infile)
    else:
        raise ValueError('{0} does not exist'.format(json_fname))


def merge_two(d1, d2):
    '''
    Merges two dictionaries into one. Second dict will overwrite values in first.

    Args:
        d1 (dict): first dictionary
        d2 (dict): second dictionary

    Returns:
        dict: A merged dictionary

    '''
    context = d1.copy()
    context.update(d2)
    return context


def rand_dictitem(d):
    '''
    Gets random item from dict

    Args:
        d(dict):

    Returns:
        tuple: dict key and value

    '''
    k = random.choice(list(d.keys()))
    return (k, d[k])


def dict_to_qs(d):
    '''
    Converts dict into query string for url

    Args:
        dict

    Returns:
        str

    '''
    return urlencode(d)


def qs_to_dict(url):
    '''
    Converts query string from url into dict with non-list values

    Args:
        url(str): url with query string

    Returns:
        dict

    '''
    qsdata = urlsplit(url).query
    return dict((k, v if len(v) > 1 else v[0])
                for k, v in parse_qs(qsdata).items())


def save_csv(data, csv_fname, fieldnames, sep=';'):
    '''
    Takes datastructure and saves as csv file

    Args:
        data (iterable): python data structure
        csv_fname (str): name of file to save
        fieldnames (list): list of fields

    Returns:
        None

    '''
    try:
        with open(csv_fname, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=sep)
            writer.writeheader()
            writer.writerows(data)
    except csv.Error:
        logging.exception('could not save csv file')


def sample_dict(d, n=1):
    '''
    Gets random sample of dictionary

    Args:
        d(dict):

    Returns:
        dict

    '''
    keys = list(d.keys())
    return {k: d[k] for k in random.sample(keys, n)}


def url_quote(s):
    '''
    Python 3 url quoting

    Args:
        s (str): string to quote

    Returns:
        str: URL quoted string

    '''
    return quote(s)


def valornone(val):
    '''

    Args:
        val:

    Returns:

    '''
    if val == '':
        return None
    else:
        return val


if __name__ == '__main__':
    pass
