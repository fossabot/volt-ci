from socketserver import BaseRequestHandler
import time
import re
import subprocess
import os
import unittest
import socket

from ci.logger import logger
from ci.utils import communicate

basedir = os.path.abspath(os.path.dirname(__file__))


class TestRunnerHandler(BaseRequestHandler):

    command_re = re.compile(r"([b])'(\w+)(:.+)*'")

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.command_groups = self.command_re.match(f"{self.data}")
        self.commands = {"ping": self.health_check, "runtest": self.runtest}
        command = self.command_groups.group(2)

        # Handle commands, if none match, handle invalid command
        self.commands.get(command, self.invalid_command)()

    def invalid_command(self):
        """
        responds to client(in this case dispatcher handler) or any other client
        that the command sent is invalid
        """
        self.request.sendall(b"Invalid command")

    def health_check(self):
        """
        Checks if the test runner server is still up & ready to accept connections
        and commands
        """
        self.server.last_communication = time.time()
        self.request.sendall(b"pong")

    def runtest(self):
        """
        This accepts messages of form runtest:<commit_id> & kicks of tests for the given commit id. 
        If the server is busy, it will respond to the dispatcher server with a BUSY response. If the
        server is not busy, it will respond with OK status & will then kick of running tests & set its
        status to BUSY
        """
        if self.server.busy:
            logger.warning("I am currently busy...")
            self.request.sendall(b"BUSY")
        else:
            logger.info("Not busy at the moment :)")
            self.request.sendall(b"OK")
            commit_id_and_branch = self.command_groups.group(3)[1:]

            c_and_b = commit_id_and_branch.split(":")
            commit_id = c_and_b[0]
            branch = c_and_b[1]

            self.server.busy = True
            self.run_tests(commit_id, branch, self.server.repo_folder)
            self.server.busy = False

    def run_tests(self, commit_id, branch, repo_folder):
        """
        Runs tests as found in the repository
        """
        output = subprocess.check_output(
            [f"{basedir}/test_runner_script.sh", repo_folder, commit_id, branch]
        )

        test_folder = os.path.join(repo_folder, "tests")
        suite = unittest.TestLoader().discover(test_folder)
        result_file = open("results", "w")
        unittest.TextTestRunner(result_file).run(suite)
        result_file.close()
        result_file = open("results", "r")

        # send results to reporter service
        output = result_file.read()

        # check that reporter service is alive & running before sending output
        # TODO: cache/retry logic to send test results to reporter service in case it is unreachable
        try:
            response = communicate(
                self.server.reporter_service["host"],
                int(self.server.reporter_service["port"]),
                "status",
            )

            if response != b"OK":
                logger.warning(
                    "Reporter Service does not seem ok, Can't send test results..."
                )
                return
            elif response == b"OK":
                logger.info(
                    "Sending test results to Reporter Service..."
                )
                communicate(
                    self.server.reporter_service["host"],
                    int(self.server.reporter_service["port"]),
                    f"results:{commit_id}:{len(output)}:{output}",
                )
        except socket.error as e:
            logger.error(
                "Cannot communicate with Reporter Service..."
            )
            return
