class TestRunnerError(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "An error occurred in TestRunner"
        super(TestRunnerError, self).__init__(msg)
