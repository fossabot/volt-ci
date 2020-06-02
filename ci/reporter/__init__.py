"""
This is the Reporter Service.

This is responsible for Reporting test results as received from test runners
"""
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from ci.logger import logger
from ci.utils import communicate


from .threading_tcp_server import ThreadingTCPServer
from .reporter_handler import ReporterHandler


def reporter_service(host, port):
    """
    Entry point to Reporter Service
    """

    server = ThreadingTCPServer((host, int(port)), ReporterHandler)

    logger.info(f"Reporter Service running on address {host}:{port}")

    try:
        # Run forever unless stopped
        server.serve_forever()
    except (KeyboardInterrupt, Exception):
        # in case it is stopped or encounters any error
        server.dead = True
