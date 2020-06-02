"""
Dispatch Handler

This is responsible for handling all requests that come in for the dispatch server
"""

import socketserver
import re
import os

from ci.logger import logger

basedir = os.path.abspath(os.path.dirname(__file__))


class ReporterHandler(socketserver.BaseRequestHandler):
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
    :cvar BUF_SIZE: buffer size
    """

    command_re = re.compile(r"([b])'(\w+)(:.+)*'")
    BUF_SIZE = 1024

    def handle(self):
        self.data = self.request.recv(self.BUF_SIZE).strip()
        self.command_groups = self.command_re.match(f"{self.data}")

        self.commands = {
            "status": self.check_status,
            "results": self.results,
        }

        if not self.command_groups:
            self.invalid_command()
            return

        command = self.command_groups.group(2)

        # Handle commands, if none match, handle invalid command
        self.commands.get(command, self.invalid_command)()

    def invalid_command(self):
        self.request.sendall(b"Invalid command")

    def check_status(self):
        """
        Checks the status of the dispatcher server
        """
        logger.info("Checking Reporter Service Status")
        self.request.sendall(b"OK")

    def results(self):
        """
        This command is used by the test runners to post back results to the dispatcher server
        it is used in the format:

        `results:<commit ID>:<length of results in bytes>:<results>`

        <commit ID> is used to identify which commit ID the tests were run against
        <length of results in bytes> is used to figure out how big a buffer is needed for the results data
        <results> holds actual result output
        """

        logger.info("Received test results from Test Runner")

        results = self.command_groups.group(3)[1:]
        results = results.split(":")

        commit_id = results[0]
        length_msg = int(results[1])

        # 3 is the number of ":" in the sent command
        remaining_buffer = self.BUF_SIZE - (
            len("results") + len(commit_id) + len(results[1]) + 3
        )

        if length_msg > remaining_buffer:
            self.data += self.request.recv(length_msg - remaining_buffer).strip()

        test_results_path = f"{basedir}/test_results"

        if not os.path.exists(test_results_path):
            os.makedirs(test_results_path)

        with open(f"{test_results_path}/{commit_id}", "w") as f:
            data = f"{self.data}".split(":")[3:]
            data = "\n".join(data)
            f.write(data)

        self.request.sendall(b"OK")
