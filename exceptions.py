class RepoObserverError(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "An error occurred in RepoObserver"
        super(RepoObserverError, self).__init__(msg)
