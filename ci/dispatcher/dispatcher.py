"""
This is the test dispatcher.

It will dispatch tests against any registered test runners when the repo
observer sends it a 'dispatch' message with the commit ID to be used. It
will store results when the test runners have completed running the tests and
send back the results in a 'results' messagee

It can register as many test runners as you like. To register a test runner,
be sure the dispatcher is started, then start the test runner.
"""
import argparse
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from utils.logger import logger
from utils import communicate
from ..utils import dispatch_tests

from .threading_tcp_server import ThreadingTCPServer
from .dispatcher_handler import DispatcherHandler


def runner_checker(server):
    """
    This will run a check(ping) against each test runner server to check if they are still responsive.
    If any of the test runners go down or become unresponsive, the runner is removed from the connection pool
    & the commit_id is dispatched to a responsive test runner. The commit_id is logged onto the pending_commits
    
    :param server: dispatcher server instance
    """

    def manage_commit_lists(runner):
        for commit, assigned_runner in server.dispathed_commits.items():
            if assigned_runner == runner:
                del server.dispatched_commits[commit]
                serve.pending_commits.append(commit)
                break
        server.runners.remove(runner)

    while not server.dead:
        time.sleep(1)

        for runner in server.runners:
            s = socket(AF_INET, SOCK_STREAM)

            try:
                response = communicate(runner["host"], int(runner["port"]), "ping")

                if response != "pong":
                    logger.warn(f"Removing runner {runner} from pool")
                    manage_commit_lists(runner)
            except socket.error as e:
                manage_commit_lists(runner)


def redistribute(server):
    """
    This is used to `redistribute` the commit_ids that are in the pending_commits `queue`(pending_commits list)
    It then calls dispatch_tests if there are pending commits
    """
    while not server.dead:
        for commit in server.pending_commits:
            logger.info(f"Redistributing pending commits {server.pending_commits} ...")
            dispatch_tests(server, commit)
            time.sleep(5)


def serve():
    """
    Entry point to dispatch server
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="Dispatchers host, defaults to localhost",
        default="localhost",
        action="store",
    )
    parser.add_argument(
        "--port",
        help="Dispatchers port, defaults to 8000",
        default=8000,
        action="store",
    )

    args = parser.parse_args()

    server = ThreadingTCPServer((args.host, int(args.port)), DispatcherHandler)

    logger.info(f"Dispatcher Server running on address {args.host}:{args.port}")

    runner_heartbeat = Thread(target=runner_checker, args=(server))
    redistributor = Thread(target=redistribute, args=(server))

    try:
        runner_heartbeat.start()
        redistributor.start()

        # Run forever unless stopped
        server.serve_forever()
    except (KeyboardInterrupt, Exception):
        # in case it is stopped or encounters any error
        server.dead = True
        runner_heartbeat.join()
        redistributor.join()


if __name__ == "__main__":
    serve()
