"""
Dispatch Handler

This is responsible for handling all requests that come in for the dispatch server
"""

import socketserver
import re
import os

from ci.logger import logger
from .utils import dispatch_tests


class DispatcherHandler(socketserver.BaseRequestHandler):
    """
    Inherits from socketserver's BaseRequestHandler

    This overrides the hande method to execute the various commands that come in from connections to the
    dispatch server.

    Compilation of the command from a Regex if first used to check if there are commands to execute
    & if nothing compiles, returns a response stating an invalid command was requested

    It then proceeds to handle the commands if the command is available & can be handled

    4 Commands are handled

    status:
    :cvar command_re: Compiled Regex of the command to handle for incoming request
    :cvar BUG_SIZE: buffer size
    """

    command_re = re.compile(r"(\w+)(:.+)*")
    BUF_SIZE = 1024

    def handle(self):
        self.data = self.request.recv(self.BUF_SIZE).strip()
        self.command_groups = self.command_re.match(self.data)
        self.commands = {
            "status": self.check_status,
            "register": self.register,
            "dispatch": self.dispatch,
            "results": self.results,
        }

        if not self.command_groups:
            self.invalid_command()
            return

        command = self.command_groups.group(1)

        # Handle commands, if none match, handle invalid command
        self.commands.get(command, self.invalid_command)()

    def invalid_command(self):
        self.request.sendall("Invalid command")

    def check_status(self):
        """
        Checks the status of the dispatcher server
        """
        logger.info("Checking Dispatch Server Status")
        self.request.sendall("OK")

    def register(self):
        """
        registers new test runners to the runners pool
        """
        logger.info("Registering new test runner")
        address = self.command_groups.group(2)
        host, port = re.findall(r":(\w*)", address)
        runner = {"host": host, "port": port}
        self.server.runners.append(runner)
        self.request.sendall("OK")

    def dispatch(self):
        """
        dispatch command is used to dispatch a commit against a test runner. When the repo
        observer sends this command as 'dispatch:<commit_id>'. The dispatcher parses the commit_id
        & sends it to a test runner
        """
        logger.info("Dispatching to test runner")
        commit_id = self.command_groups.group(2)[1:]

        if not self.server.runners:
            self.request.sendall("No runners are registered")
        else:
            # we can dispatch tests, we have at least 1 test runner available
            self.request.sendall("OK")
            dispatch_tests(self.server, commit_id)

    def results(self):
        """
        This command is used by the test runners to post back results to the dispatcher server
        it is used in the format:

        `results:<commit ID>:<length of results in bytes>:<results>`

        <commit ID> is used to identify which commit ID the tests were run against
        <length of results in bytes> is used to figure out how big a buffer is needed for the results data
        <results> holds actual result output
        """

        logger.info("got test results")

        results = self.command_groups.group(2)[1:]
        results = results.split(":")

        commit_id = results[0]
        length_msg = int(results[1])

        # 3 is the number of ":" in the sent command
        remaining_buffer = self.BUF_SIZE - (
            len("results") + len(commit_id) + len(results[1]) + 3
        )

        if length_msg > remaining_buffer:
            self.data += self.request.recv(length_msg - remaining_buffer).strip()

        del self.server.dispatched_commits[commit_id]

        if not os.path.exists("test_results"):
            os.makedirs("test_results")

        with open(f"test_results/{commit_id}", w) as f:
            data = self.data.split(":")[3:]
            data = "\n".join(data)
            f.write(data)

        self.request.sendall("OK")
