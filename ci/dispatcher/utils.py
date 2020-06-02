"""
Dispatcher Utils

Contains util functions re-usable in dispatcher server
"""
import time

from ci.logger import logger
from ci.utils import communicate


def dispatch_tests(server, commit_id, branch):
    """
    Dispatches tests to test runners

    :param server: dispatcher server
    :param commit_id: commit id to dispatch to test runners
    :param branch: branch to run tests on
    """

    while True:
        logger.info(
            f"Attempting to dispatch commit {commit_id} on branch {branch} to runners..."
        )

        for runner in server.runners:
            response = communicate(
                runner["host"], int(runner["port"]), f"runtest:{commit_id}:{branch}"
            )

            if response == b"OK":
                logger.info(
                    f"Adding ID: {commit_id} for branch {branch} to Runner: {runner['host']}:{runner['port']}"
                )

                server.dispatched_commits[commit_id] = runner

                if commit_id in server.pending_commits:
                    server.pending_commits.pop(commit_id, None)
                return
        time.sleep(2)
