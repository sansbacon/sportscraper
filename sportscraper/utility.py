'''
nfl/utility.py

Utility functions for nfl library

'''

import collections
import csv
import json
import logging
from lxml import etree, html
import os
import random
from functools import wraps
from urllib.parse import urlsplit, parse_qs, urlencode, quote

try:
    import cPickle as pickle
except ImportError:
    import pickle


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


def dict_to_csv(dicts, fn, fields=None):
    '''
    Writes list of dict to csv file. Can specify fields or use keys for dicts[0].

    Args:
        dicts(list): of dict
        fn(str): name of csvfile
        fields(list): fieldnames, default None

    Returns:
        None

    '''
    with open(fn, 'w') as csvfile:
        if not fields:
            fields = list(dicts[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for dict_to_write in dicts:
            writer.writerow(dict_to_write)


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


def file_to_ds(fname):
    '''
    Pass filename, it returns data structure based on file extension.

    Args:
        fname (str): filename

    Returns:
        data structure

    '''
    ext = os.path.splitext(fname)[1]
    if ext == '.csv':
        data_structure = csv_to_dict(fname)
    elif ext == '.json':
        data_structure = json_to_dict(fname)
    elif ext == 'pkl':
        data_structure = read_pickle(fname)
    else:
        raise ValueError('%s is not a supported file extension' % ext)
    return data_structure


def isfloat(x):
    '''
    Tests if conversion to float succeeds

    Args:
        x: value to test

    Returns:
        boolean: True if can convert to float, False if cannot.

    '''
    try:
        return float(x)
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


def memoize(function):
    '''
    Memoizes function

    Args:
        function (func): the function to memoize

    Returns:
        func: A memoized function

    '''
    memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        retval = function(*args)
        memo[args] = retval
        return retval
    return wrapper


def merge(merge_dico, dico_list):
    '''
    Merges multiple dictionaries into one

    Note:
        See http://stackoverflow.com/questions/28838291/merging-multiple-dictionaries-in-python

    Args:
        merge_dico (dict): dict to merge into
        dico_list (list): list of dict

    Returns:
        dict: merged dictionary

    '''
    for dico in dico_list:
        for key, value in dico.items():
            if isinstance(value, dict):
                merge_dico.setdefault(key, dict())
                merge(merge_dico[key], [value])
            else:
                merge_dico[key] = value
    return merge_dico


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


def pair_list(list_):
    '''
    Allows iteration over list two items at a time
    '''
    list_ = list(list_)
    return [list_[i:i + 2] for i in range(0, len(list_), 2)]


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


def read_pickle(pkl_fname):
    '''
    Takes pickle file and returns data structure

    Args:
        pkl_fname (str): name of file to read/parse

    Returns:
        iterable: python datastructure

    '''
    if os.path.exists(pkl_fname):
        with open(pkl_fname, 'rb') as infile:
            return pickle.load(infile)
    else:
        raise ValueError('{0} does not exist'.format(pkl_fname))


def read_json(json_fname):
    '''
    Reads json file

    Arguments:
        json_fname (str): name of file to save

    Returns:
        dict

    '''
    try:
        with open(json_fname, 'r') as infile:
            return json.load(infile)
    except json.JSONDecodeError:
        logging.exception('%s does not exist', json_fname)


def save_json(data, json_fname):
    '''
    Takes data and saves to json file

    Arguments:
        data (iterable): python data structure
        json_fname (str): name of file to save

    Returns:
        None

    '''
    try:
        with open(json_fname, 'w') as outfile:
            json.dump(data, outfile)
    except json.JSONDecodeError:
        logging.exception('%s does not exist', json_fname)


def save_pickle(data, pkl_fname):
    '''
    Saves data structure to pickle file

    Args:
        data (iterable): python data structure
        pkl_fname (str): name of file to save

    Returns:
        None

    '''
    try:
        with open(pkl_fname, 'wb') as outfile:
            pickle.dump(data, outfile)
    except pickle.PickleError:
        logging.exception('%s does not exist', pkl_fname)


def save_file(data, fname):
    '''
    Pass filename, it returns datastructure. Decides based on file extension.

    Args:
        data (iterable): arbitrary datastructure
        fname (str): filename to save

    Returns:
        None
    '''
    ext = os.path.splitext(fname)[1]
    if ext == '.csv':
        save_csv(data=data, csv_fname=fname, fieldnames=data[0])
    elif ext == '.json':
        save_json(data, fname)
    elif ext == 'pkl':
        save_pickle(data, fname)
    else:
        raise ValueError('{} is not a supported file extension'.format(ext))


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