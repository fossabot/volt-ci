from socketserver import ThreadingMixIn, TCPServer


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    """
    Custom TCP Server which allows spawning of threads to allow requests to be handled on different threads

    :cvar dispatcher_server: Holds the dispatcher server host/port information
    :cvar reporter_service: Holds the dispatcher server host/port information
    :cvar last_communication: Keeps track of last communication from dispatcher
    :cvar busy: Status flag indicating whether the test runner server is currently busy
    :cvar dead: Status flag indicating whether this test runner server is dead/unresponsive
    """

    dispatcher_server = None
    reporter_service = None
    last_communication = None
    busy = False
    dead = False
