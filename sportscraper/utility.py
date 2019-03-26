"""
utility.py

Utility functions for sportscraper library

"""

import collections
import csv
import json
import logging
import os
import random
import string
from urllib.parse import urlsplit, parse_qs, urlencode, quote


LOGGER = logging.getLogger(__name__)


def csv_to_dict(filename):
    """
    Takes csv filename and returns dicts

    Arguments:
        filename (str): name of file to read/parse

    Returns:
        list: List of dicts

    """
    with open(filename, "r") as infile:
        for row in csv.DictReader(infile, skipinitialspace=True, delimiter=","):
            yield {k: v for k, v in row.items()}


def digits(numstr):
    """
    Removes non-numeric characters from a string

    Args:
        numstr (str): string with non-numeric characters

    Returns:
        str

    """
    return "".join(ch for ch in numstr if ch.isdigit())


def flatten(nested_dict):
    """
    Flattens nested dict into single dict

    Args:
        nested_dict (dict): The original dict

    Returns:
        dict: nested dict flattened into dict

    """
    items = []
    for key, val in nested_dict.items():
        if isinstance(val, collections.MutableMapping):
            items.extend(flatten(val).items())
        else:
            items.append((key, val))
    return dict(items)


def flatten_list(nested_list):
    """
    Flattens list of lists into list

    Args:
        nested_list (list): original list of lists

    Returns:
        list

    """
    try:
        return [item for sublist in nested_list for item in sublist]
    except TypeError:
        return nested_list


def isfloat(val):
    """
    Tests if conversion to float succeeds

    Args:
        x: value to test

    Returns:
        boolean: True if can convert to float, False if cannot.

    TODO: this is broken
    """
    try:
        _ = float(val)
        return True
    except ValueError:
        return False


def isint(val):
    """
    Tests if value is integer

    Args:
        x: value to test

    Returns:
        boolean: True if int, False if not.

    TODO: this is broken
    """
    try:
        val_float = float(val)
        val_int = int()
        return val_float == val_int
    except ValueError:
        return False


def json_to_dict(json_fname):
    """
    Takes json file and returns data structure

    Args:
        json_fname (str): name of file to read/parse

    Returns:
        dict: Parsed json into dict

    """
    if os.path.exists(json_fname):
        with open(json_fname, "r") as infile:
            return json.load(infile)
    else:
        raise ValueError("{0} does not exist".format(json_fname))


def merge_two(dict1, dict2):
    """
    Merges two dictionaries into one. Second dict will overwrite values in first.

    Args:
        dict1 (dict): first dictionary
        dict2 (dict): second dictionary

    Returns:
        dict: A merged dictionary

    """
    context = dict1.copy()
    context.update(dict2)
    return context


def rand_dictitem(dict_to_sample):
    """
    Gets random item from dict

    Args:
        d(dict):

    Returns:
        tuple: dict key and value

    """
    k = random.choice(list(dict_to_sample.keys()))
    return (k, dict_to_sample[k])


def dict_to_qs(dict_to_convert):
    """
    Converts dict into query string for url

    Args:
        dict_to_convert(dict)

    Returns:
        str

    """
    return urlencode(dict_to_convert)


def qs_to_dict(url):
    """
    Converts query string from url into dict with non-list values

    Args:
        url(str): url with query string

    Returns:
        dict

    """
    qsdata = urlsplit(url).query
    return dict(
        (key, val if len(val) > 1 else val[0]) for key, val in parse_qs(qsdata).items()
    )


def random_string(string_length):
    """
    Generates random string of specified length

    Args:
        string_length(int):

    Returns:
        str

    """
    if string_length > 32:
        string_length = 32
    return "".join(
        [
            random.choice(string.ascii_letters + string.digits)
            for _ in range(string_length)
        ]
    )


def save_csv(data, csv_fname, fieldnames, sep=";"):
    """
    Takes datastructure and saves as csv file

    Args:
        data (iterable): python data structure
        csv_fname (str): name of file to save
        fieldnames (list): list of fields

    Returns:
        None

    """
    try:
        with open(csv_fname, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=sep)
            writer.writeheader()
            writer.writerows(data)
    except csv.Error:
        logging.exception("could not save csv file")


def sample_dict(dict_to_sample, size=1):
    """
    Gets random sample of dictionary

    Args:
        dict_to_sample(dict):
        size(int): size of sample

    Returns:
        dict

    """
    keys = list(dict_to_sample.keys())
    return {k: dict_to_sample[k] for k in random.sample(keys, size)}


def url_quote(str_to_quote):
    """
    Python 3 url quoting

    Args:
        str_to_quote (str): string to quote

    Returns:
        str: URL quoted string

    """
    return quote(str_to_quote)


def valornone(val):
    """

    Args:
        val:

    Returns:

    """
    if val == "":
        return None
    return val


if __name__ == "__main__":
    pass
