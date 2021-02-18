from functools import lru_cache
from pathlib import Path
import os
from random import sample, shuffle
from itertools import cycle
import urllib.request
from urllib.parse import urlparse

from dotenv import load_dotenv
import csv
import json
import requests
import re

"""
    Spam naughty stuff on map.

    Uses har files to describe how data is handled. Generating that file takes
    some covert ops, namely filling page with data describet in `NONNAUGHTY_WORDS`.
    https://toolbox.googleapps.com/apps/har_analyzer/

    Agora coordinates are replaced with ones from NAUGHTY_COORDS.

    TODO: Handle missing HAR files
    TODO: Handle non-latin1 characters.
"""

LDNOOBW_DIR = path = Path(__file__).parent.absolute() / "ldnoobw"
LDNOOBW_LANGS = [str(p.name) for p in Path(LDNOOBW_DIR).glob("??")]

# `har`s are transaction logs form webbrowsers.
HARS_DIR = Path(__file__).parent.absolute() / "hars"

# Non-naughty words in post data to be replaced with naughty ones
NONNAUGHTY_WORDS = [
    "Richard",
    "Clunis",
    # "fellowhuman",
    # "notcylons",
    "Agora",
    "Pekka",
    "Neittaanmäki",
]

NAUGHTY_COORDS = [
    (2.6458333, 11.90625),
    (3.96875, 11.1125),
    (5.8208333, 10.054167),
    (8.2020832, 8.7312499),
    (10.583333, 7.6729166),
    (12.435417, 6.8791666),
    (15.081249999999999, 5.820833299999999),
    (16.933332999999998, 5.291666599999999),
    (18.785415999999998, 5.027083299999999),
    (20.6375, 5.291666599999999),
    (21.695833, 6.085416599999999),
    (22.225, 7.4083331999999995),
    (21.960416000000002, 8.4666666),
    (21.166666000000003, 9.2604166),
    (20.108333000000002, 9.5249999),
    (18.785416, 9.2604166),
    (17.197916000000003, 9.7895832),
    (15.081250000000002, 10.847916999999999),
    (12.964583000000003, 12.170832999999998),
    (11.377083000000002, 13.229166999999999),
    (9.524999900000003, 14.552082999999998),
    (7.937499900000002, 15.874999999999998),
    (9.260416600000003, 16.404165999999996),
    (10.054167000000003, 16.933332999999998),
    (11.112500000000002, 17.727082999999997),
    (11.641667000000002, 19.049999999999997),
    (11.377083000000002, 20.637499999999996),
    (10.847917000000002, 22.224999999999994),
    (9.789583200000003, 23.018749999999994),
    (8.202083200000002, 23.547915999999994),
    (6.614583200000002, 23.283332999999992),
    (5.2916666, 22.754166),
]


def mikkelitit(points):
    offset = (26.277328931661287, 62.68537225878102)

    # Reposition <- scale <- flip svg to mercorator
    # TODO: Fix projection
    locations = [
        (x + offset[0], y + offset[1])  # Set offset
        for (x, y) in (
            (x * 0.1, y * 0.1)  # Scale
            for (x, y) in (
                (x, -1 * y)  # Flip SVG coordinates vertically
                for (x, y) in points
            )
        )
    ]
    return locations


def read_badwords(langs=["en", "fi"]):
    """ Read bad words for langs from ldnoobw dir """

    @lru_cache(maxsize=64)
    def _read_file(filepath):
        with Path(filepath).open() as fd:
            r = filter(None, map(str.strip, fd.readlines()))
        return r

    words = []
    for lang in set(langs):
        words += _read_file(Path(LDNOOBW_DIR) / lang)

    return words


def naughty_words():
    """Return naughty words form english, finnish, and possibly third random language

    Warning: Generates infinite list
    """
    words = list(set(read_badwords(["en", "fi"] + sample(LDNOOBW_LANGS, 1))))
    shuffle(words)
    return cycle(words)


def team_deployments(csv_path):
    """Read deployments from CSV file.

    File can be direct file, or url
    """

    def read_csv_for_deployments(csv_path):
        with Path(csv_path).open() as fd:
            urls = [row["DEPLOYMENT"] for row in csv.DictReader(fd)]
        return urls

    deployment_urls = []
    if urlparse(csv_path).scheme != "":
        # Download and parse file
        (path, status) = urllib.request.urlretrieve(csv_path)
        deployment_urls += read_csv_for_deployments(path)
    else:
        deployment_urls += read_csv_for_deployments(csv_path)

    return deployment_urls


def find_har_file(url, folder=HARS_DIR):
    """ Find `.har` file matching url from :param:`folder` directory """
    domain = urlparse(url).netloc.lower()
    return next(Path(folder).glob(f"{domain}_*.har"))


def prepare_replay_data(harfile):
    with Path(harfile).open() as fd:
        data = json.load(fd)

    request = data["log"]["entries"][0]["request"]

    post_data = request["postData"]
    word_list = naughty_words()

    for boring_word in NONNAUGHTY_WORDS:
        # Replace words
        funny_word = next(word_list)
        if boring_word[0].isupper():
            funny_word = funny_word.capitalize()

        post_data["text"] = post_data["text"].replace(boring_word, funny_word)

    return request


def acate(deployment, dry_run=True):
    """ Send bunch of coordinates to deployment. """
    headers = {}
    cookies = {}

    # Find har file to use as basis for data replay.
    har_file = find_har_file(deployment)
    req = prepare_replay_data(har_file)

    print("Defacating %s" % deployment)

    # Copy (some) headers.
    for _header in req['headers']:
        print("HEADER:\t", _header)
        if _header['name'] in ['Referer', 'User-Agent', 'Content-Type']:
            headers[_header['name']] = _header['value']

    cookies = {c['name']: c['value'] for c in req['cookies']}

    post_data = req["postData"]["text"]

    for (x, y) in mikkelitit(NAUGHTY_COORDS):
        # Replace agora coordinates
        x, y = (str(x), str(y))
        point_post_data = re.sub(r'(?![^\d])(25\.\d*)', x, re.sub(r'(?![^\d])(62\.\d*)', y, post_data))

        if dry_run:
            r = "<TEST>"
        else:
            # Lucky us, everyone is using POST
            r = requests.post(
                req['url'],
                params=req["postData"]["params"],
                data=point_post_data,
                headers=headers,
                cookies=cookies
            )

        # Print debug info
        print((x, y), point_post_data, r)


if __name__ == "__main__":
    load_dotenv("../.env")

    #deployments = ["https://agile-team-299406.ew.r.appspot.com/"]
    deployments = team_deployments(os.getenv('TEAMS_REPOSITORIES_CSV'))

    for deployment in deployments:
        # TODO: Handle missing HAR resources.
        acate(deployment)
