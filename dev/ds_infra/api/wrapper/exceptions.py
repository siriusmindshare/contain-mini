class ProjectException(Exception):
    """Exception raised for errors in the project.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg


class FrameworkException(Exception):
    """Exception raised for errors in the project.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
