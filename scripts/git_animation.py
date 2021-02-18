import gitlab
import subprocess
import shlex
import urllib.request
from pathlib import Path
import sys

import moviepy.editor as mpy
import multiprocessing

from functools import lru_cache, partial
import logging
import os
import concurrent
import time
import random

import requests
import requests_cache
requests_cache.install_cache()


gl = gitlab.Gitlab('https://gitlab.jyu.fi', private_token=os.getenv("GITLAB_TOKEN"))

# Some forks that are not interesting
FORKS_DENIED = [2034, 1739, 1833, 1956, 2030]

RESOLUTION = (1920, 1080)
GRID = (5, 3)
FPS = 30

logging.basicConfig(level=logging.DEBUG)

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
    logging.debug("Searching committer avatar for username %s", username)
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
        # Lock file is to prevent similar requests being spammed when avatar is missing.
        target_lock = target_path / (Path(author + ".lock")).name
        target = target_path / (Path(author + ".png")).name

        if target_lock.exists() or target.exists():
            continue
        else:
            target_lock.touch()

        avatar_url = search_committer_avatar(email, author)
        if not avatar_url:
            logging.warning("Didn't find image for %s" % author)
            continue

        print("Fetching avatar", avatar_url, target)
        try:
            urllib.request.urlretrieve(avatar_url, target)
        except Exception:
            logging.exception("Could not retrieve avatar for %s (%s)", author, avatar_url, exc_info=True)


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
    # Multiply fps by this to speed up animation generation
    fast_forward = 2

    fps = str(FPS)
    ff_fps = str(FPS * fast_forward) 

    size = "-%dx%d" % (RESOLUTION[0] / GRID[0], RESOLUTION[1] / GRID[1])
    # Gource is responsible of creating video
    gource = ["gource",
        "--disable-auto-skip",
        "--elasticity", "0.3",
        "-s", str(5 / fast_forward),
        "-r", ff_fps,
        "--stop-position", "1.0",
        "--highlight-all-users",
        "--camera-mode", "overview",
        size,
        "--multi-sampling",
        "--background-colour", "000000",
        "--disable-progress",
        "--hide mouse",
        "--output-ppm-stream -",
    ] + gource_params + [shlex.quote(str(git_dir))]

    # ffmpeg converts gource output into a file
    ffmpeg = ["ffmpeg",
        "-y",
        "-r", ff_fps,
        "-f", "image2pipe",
        "-vcodec", "ppm",
        "-i", "-",
        "-vcodec", "libvpx",
        "-b", "3000K",
        "-r", fps,
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


def process_fork(path, fork):
    logging.info("Processing fork %s" % fork)
    target = Path(path)

    avatars_path = target / "avatars"
    fork_path = target / str(fork)
    video_path = target / ("%d.mkv" % fork)

    logging.debug("Cloning git...")
    git_clone_project(fork, fork_path)

    logging.debug("Fetching avatars...")
    fetch_repo_avatars(fork_path, avatars_path)

    for _ in range(5):
        # We might hit rate limiter, so try couple of times.
        try:
            project = gl.projects.get(fork)
            title = project.name
            break
        except Exception as e:
            _wait = random.randint(1, 5)
            logging.info("Project info retrieval failed, waiting %d seconds.", _wait)
            logging.debug("%s", e)
            time.sleep(_wait)
    else:
        raise RuntimeError("Could not retrieve project info after multiple attempts.")

    generate_animation(fork_path, video_path, avatars_path, gource_params=["--title", shlex.quote(title), "--start-date", "2021-01-12"])

    return video_path


if __name__ == "__main__":

    target = Path(sys.argv[1])

    if not target.exists():
        raise FileNotFoundError("Target path %r doesn't exists" % target)

    # 1839 is an indirect fork -> fork from a fork
    additional = [
        # 1674, # beeMapTemplate
        1839,   # beeMapDevWarriors
        1947,   # beeMapSpark
    ]

    forks = set(filter(lambda id: id not in FORKS_DENIED, project_forks(1674) + additional))

    videos = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Convert into list to force evaluation
        videos = list(executor.map(partial(process_fork, target), forks))

    compiled_video = target / "compiled.webm"
    generate_video_wall(videos, compiled_video)
