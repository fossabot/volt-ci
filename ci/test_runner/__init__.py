"""
Test Runner

Responsible for running tests against a commit_id as received from dispatcher server. Will communicate with 
dispatcher server on the tests results for each test run against a commit id
"""
import socket
import errno
import time
from threading import Thread

from ci.logger import logger
from .threading_tcp_server import ThreadingTCPServer
from .exceptions import TestRunnerError
from .test_runner_handler import TestRunnerHandler
from ci.utils import communicate


def dispatcher_checker(server):
    """
    This is used to check on the dispatcher checker. If the dispatcher checker goes down for any reason, then there
    is no need to have the test runner server running, as it will have no commands coming in from dispatcher server
    & it will have nowhere to send reports to. This is to conserve on resources. This is run every 5 seconds
    """

    while not server.dead:
        time.sleep(5)
        if (time.time() - server.last_communication) > 10:
            try:
                response = communicate(
                    server.dispatcher_server["host"],
                    int(server.dispatcher_server["port"]),
                    "status",
                )

                if response != b"OK":
                    logger.warning("Dispatcher Server does not seem ok, shutting down...")
                    server.shutdown()
                    return
            except socket.error as e:
                logger.warning("Cannot communicate with Dispatcher Server, shutting down...")
                server.shutdown()
                return


def test_runner_server(host, port, repo, dispatcher_host, dispatcher_port):
    """
    This invokes the Test Runner server.

    :param host: host to use
    :param port: port to use
    :param repo: repository to watch
    """
    range_start = 8900

    runner_host = host
    runner_port = None
    tries = 0

    if not port:
        runner_port = range_start

        while tries < 100:
            try:
                logger.info(f"TestRunner Server running on address -> {runner_host}:{runner_port}")
                server = ThreadingTCPServer(
                    (runner_host, runner_port), TestRunnerHandler
                )
                break
            except socket.error as e:
                logger.error(f"Error starting server, {e}")
                if e.errno == errno.EADDRINUSE:
                    tries += 1
                    runner_port = runner_port + tries
                    continue
                else:
                    raise e
        else:
            raise TestRunnerError(
                f"Could not bind to ports in range {range_start}-{range_start+tries}"
            )
    else:
        runner_port = int(port)
        logger.info(f"TestRunner Server running on address -> {runner_host}:{runner_port}")
        server = ThreadingTCPServer((runner_host, runner_port), TestRunnerHandler)

    server.repo_folder = repo

    server.dispatcher_server = {"host": dispatcher_host, "port": dispatcher_port}
    response = communicate(
        server.dispatcher_server["host"],
        int(server.dispatcher_server["port"]),
        f"register:{runner_host}:{runner_port}",
    )
    if response != b"OK":
        logger.error(f"Cannot register with dispatcher: {response}")
        raise TestRunnerError("Can't register with dispatcher!")

    thread = Thread(target=dispatcher_checker, args=(server,))

    try:
        thread.start()
        # this will run unless stopped by keyboard interrupt or by an exception
        server.serve_forever()
    except (KeyboardInterrupt, Exception):
        server.dead = True
        thread.join()
