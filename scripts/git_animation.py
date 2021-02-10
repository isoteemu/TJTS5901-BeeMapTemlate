import requests
from collections import namedtuple
import csv
from datetime import datetime
import gitlab
import subprocess
import shlex
import urllib.request
from pathlib import Path
import sys

import moviepy.editor as mpy
import multiprocessing

from functools import lru_cache
import logging
import os

# I've uploaded secrets. Don't worry, its revoked.
gl = gitlab.Gitlab('https://gitlab.jyu.fi', private_token=os.getenv("GITLAB_TOKEN"))

# Some forks that are not interesting
FORKS_DENIED = [2034, 1739, 1833, 1956, 2030]

RESOLUTION = (1920, 1080)
GRID = (5, 3)
FPS = 25


def git_authors(path):
    """ Fetch git authors. Return list of email and name vectors """

    git_output = subprocess.check_output(["git", "-C", str(path), "log", "--pretty=%ae|%an"], universal_newlines=True)
    committers = map(lambda x: x.split("|"), filter(None, set(git_output.split("\n"))))

    return committers


def search_committer_avatar(*args):
    """ Takes a list of possible names, and try looking them up from gitlab """

    for username in args:
        avatar_url = _search_committer_avatar(username)
        if avatar_url:
            return avatar_url
    return None


@lru_cache(maxsize=256)
def _search_committer_avatar(username):
    """ Try looking for a single user avatar from gitlab """
    search_result = gl.users.list(search=username)
    if not len(search_result):
        return None
    for user in search_result:
        if user.avatar_url:
            return user.avatar_url


def fetch_repo_avatars(repo_path, target_path):
    """ Fetch users from git logs, and download avatar from gitlab. """
    target_path = Path(target_path)
    if not target_path.exists():
        raise FileNotFoundError("Target path %r doesn't exists" % target_path.absolute())

    authors = git_authors(repo_path)

    for email, author in authors:
        target = target_path / (Path(author + ".png")).name
        if target.exists():
            continue

        avatar_url = search_committer_avatar(email, author)
        if not avatar_url:
            logging.warning("Didn't find image for %s" % author)
            continue

        print("Fetching avatar", avatar_url, target)
        urllib.request.urlretrieve(avatar_url, target)


def project_forks(project_id):
    return [fork.id for fork in gl.projects.get(project_id).forks.list()]


def git_clone_project(project_id, target_path):
    target_path = Path(target_path)

    if target_path.exists():
        logging.debug("Git target %r exists" % target_path.absolute())
        subprocess.run(["git", "-C", str(target_path), "pull"])
    else:
        url = gl.projects.get(project_id).ssh_url_to_repo
        subprocess.run(["git", "clone", url, str(target_path)])


def generate_animation(git_dir, target, avatars_dir=None, gource_params=[]):
    _FPS = str(FPS)

    size = "-%dx%d" % (RESOLUTION[0] / GRID[0], RESOLUTION[1] / GRID[1])
    # Gource is responsible of creating video
    gource = ["gource",
        "--disable-auto-skip",
        "--elasticity", "0.3",
        "-s", "5",
        "-r", _FPS,
        "--stop-position", "1.0",
        "--highlight-all-users",
        size,
        "--multi-sampling",
        "--disable-progress",
        "--hide mouse",
        "--output-ppm-stream -",
    ] + gource_params + [shlex.quote(str(git_dir))]

    # ffmpeg converts gource output into a file
    ffmpeg = ["ffmpeg",
        "-y",
        "-r", _FPS,
        "-f", "image2pipe",
        "-vcodec", "ppm",
        "-i", "-",
        "-vcodec", "libvpx",
        "-b", "3000K",
        "-r", _FPS,
        shlex.quote(str(target))
    ]

    avatars_dir = Path(avatars_dir)
    if avatars_dir.exists():
        gource += ["--user-image-dir", shlex.quote(str(avatars_dir.absolute()))]

    gource_cmd = " ".join(gource)
    ffmpeg_cmd = " ".join(ffmpeg)
    print(gource_cmd, ffmpeg_cmd)
    subprocess.run(gource_cmd + " | " + ffmpeg_cmd, shell=True)

    #subprocess.run(f"{gource_cmd!s} | {ffmpeg_cmd!s}", shell=True)


def generate_video_wall(videos, output_target):
    video_grid = []
    for row_i in range(GRID[1]):
        row = []
        for col_i in range(GRID[0]):
            try:
                row.append(mpy.VideoFileClip(str(videos.pop())))
            except IndexError:
                # Videos weren't divided evenly
                logging.warning("Videos weren't divided evenly")

        video_grid.append(row)
    output = mpy.clips_array(video_grid)

    threads = multiprocessing.cpu_count()

    return output.write_videofile(str(output_target), audio=False, threads=threads, fps=FPS, preset="veryfast", ffmpeg_params=["-b", "3000K"])


if __name__ == "__main__":
    target = Path(sys.argv[1])

    if not target.exists():
        raise FileNotFoundError("Target path %r doesn't exists" % target)

    avatars_path = target / "avatars"

    # 1839 is an indirect fork -> fork from a fork
    forks = filter(lambda id: id not in FORKS_DENIED, project_forks(1674) + [1839, 1674])

    videos = []

    for fork in forks:
        fork_path = target / str(fork)
        video_path = target / "%d.mkv" % fork
        # git_clone_project(fork, fork_path)
        # fetch_repo_avatars(fork_path, avatars_path)

        # project = gl.projects.get(fork)
        # title = project.name

        # generate_animation(fork_path, video_path, avatars_path, gource_params=["--title", shlex.quote(title), "--start-date", "2021-01-12"])
        videos.append(video_path)

    compiled_video = target / "compiled.webm"
    generate_video_wall(videos, compiled_video)
