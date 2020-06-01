from socketserver import BaseRequestHandler
import time
import re
import subprocess
import os
import unittest

from ci.logger import logger
from ci.utils import communicate


class TestRunnerHandler(BaseRequestHandler):

    command_re = re.compile(r"(\w+)(:.+)*")

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.command_groups = self.command_re.match(self.data)
        self.commands = {"ping": self.health_check, "runtest": self.runtest}
        command = command_groups.group(1)

        # Handle commands, if none match, handle invalid command
        self.commands.get(command, self.invalid_command)()

    def invalid_command(self):
        """
        responds to client(in this case dispatcher handler) or any other client
        that the command sent is invalid
        """
        self.request.sendall("Invalid command")

    def health_check(self):
        """
        Checks if the test runner server is still up & ready to accept connections
        and commands
        """
        self.server.last_communication = time.time()
        self.request.sendall("pong")

    def runtest(self):
        """
        This accepts messages of form runtest:<commit_id> & kicks of tests for the given commit id. 
        If the server is busy, it will respond to the dispatcher server with a BUSY response. If the
        server is not busy, it will respond with OK status & will then kick of running tests & set its
        status to BUSY
        """
        if self.server.busy:
            logger.warning("I am currently busy...")
            self.request.sendall("BUSY")
        else:
            logger.info("Not busy at the moment :)")
            self.request.sendall("OK")
            commit_id = self.command_groups.group(2)[1:]
            self.server.busy = True
            self.run_tests(commit_id, self.server.repo_folder)
            self.server.busy = False

    def run_tests(self, commit_id, repo_folder):
        """
        Runs tests as found in the repository
        """
        output = subprocess.check_output(
            ["./test_runner_script.sh", repo_folder, commit_id]
        )

        test_folder = os.path.join(repo_folder, "tests")
        suite = unittest.TestLoader().discover(test_folder)
        result_file = open("results", "w")
        unittest.TextTestRunner(result_file).run(suite)
        result_file.close()
        result_file = open("results", "r")

        # send results to dispatcher
        output = result_file.read()
        communicate(
            self.server.dispatcher_server["host"],
            int(self.dispather_server["port"]),
            f"results:{commit_id}:{len(output)}:{output}",
        )
