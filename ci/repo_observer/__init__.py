"""
Repo Observer

It checks for new commits to the master repo, and will notify the dispatcher of
the latest commit ID, so the dispatcher can dispatch the tests against this
commit ID. This has been simplified to only dispatch the latest commit ID to the dispatcher
& not subsequent commit IDs. This will continuously poll the repository to check for any new commits. Usually, a 
typical repo observer will receive notifications from the Repository, but some VCS systems do not have built in
notification systems.
"""
import os
import re
import socket
import socketserver
import subprocess
import sys
import time

from .exceptions import RepoObserverError
from ci.utils import communicate
from ci.logger import logger

basedir = os.path.abspath(os.path.dirname(__file__))


def observer(dispatcher_host, dispatcher_port, repo, poll, branch):
    """
    Repo Observer that communicates with the dispatcher server to send tests that are found
    on the repository on new changes commited to the repo. This will watch the repo every 5 seconds for any
    new commit that is made & make a dispatch to the dispatch server to initiate running of new tests.
    """
    logger.info(f"Running Repo Observer")
    while True:
        try:
            # call the bash script that will update the repo and check
            # for changes. If there's a change, it will drop a .commit_id file
            # with the latest commit in the current working directory
            logger.info(f"cloning repo {repo}")
            subprocess.check_output([f"{basedir}/update_repo.sh", repo, branch])
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update & check repo {repo}, err: {e.output}")
            raise RepoObserverError(
                f"Could not update & check repository. Err: {e.output}"
            )

        commit_id_file = f"{basedir}/.commit_id"
        if os.path.isfile(commit_id_file):
            # great, we have a change! let's execute the tests
            # First, check the status of the dispatcher server to see
            # if we can send the tests
            try:
                logger.info(
                    f"Checking dispatcher server status {dispatcher_host}:{dispatcher_port}"
                )
                response = communicate(dispatcher_host, int(dispatcher_port), "status")
            except socket.error as e:
                logger.error(
                    f"Dispather Server Contact error. Is Dispatcher running? err: {e}"
                )
                raise RepoObserverError(f"Could not contact dispatcher {e}")

            if response == b"OK":
                # Dispatcher is available
                commit = ""

                with open(commit_id_file) as commit_file:
                    commit = commit_file.readline()

                response = communicate(
                    dispatcher_host, int(dispatcher_port), f"dispatch:{commit}:{branch}"
                )

                if response != b"OK":
                    logger.error(
                        f"Failed to dispatch test to dispatcher. Is Dispatcher OK? err: {response}"
                    )
                    raise RepoObserverError(f"Could not dispatch test: {response}")
                logger.info(f"Dispatched tests for {repo}!")
            else:
                # Dispatcher has an issue
                raise RepoObserverError(f"Could not dispatch test {response}")

        time.sleep(poll)
