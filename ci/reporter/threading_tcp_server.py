"""
Custom Socket TCP Server to handle mutliple connections. Typically TCP servers can only handle
1 connection at a time. This is not ideal in this case, because there could be an instance where
a test runner has a connection open with the dispatcher & a connection comes in from the repo_observer.
The repo observer has to wait for the initial connection to disconnect & close, before it can proceed
with its request.

In order to handle multiple requests, this adds threading ability to the SocketServer in order to service
multiple connections on different threads.
"""
import socketserver


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Custom Threading TCP Server which ensures that there is continuous, ordered streams
    of data between servers. UDP does not ensure this

    :cvar dead: indicate to other threads that we ain't alive
    """

    dead = False
