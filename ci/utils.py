"""
Utils

Will contain common utility or helper functions that will be re-useable and used across the system
"""
from socket import socket


def communicate(host, port, request):
    """
    Handles communication with remote sockets providing the host port & request 
    to send to a remote socket connection.
    Returns response as received from remote socket
    :param host: Host address
    :param port: Port to connect to
    :param request: Request to send to remote host
    :return: Returns response in form of bytes with a buffer size of 1024 as recevied from host connection
    :rtype: bytes
    """
    s = socket()
    s.connect((host, port))
    s.send(request)
    response = s.recv(1024)
    s.close()
    return response
