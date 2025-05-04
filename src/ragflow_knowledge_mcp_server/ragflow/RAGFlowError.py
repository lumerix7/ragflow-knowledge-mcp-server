"""RAGFlowError.py"""


class RAGFlowError(Exception):
    """Base exception for all RAGFlow-related errors.

    This error extends the standard Exception class and adds a code attribute to represent HTTP-like status codes.

    Properties:
        code (int | None): An optional error code, typically an HTTP status code.
    """

    code: int | None = None

    def __init__(self, message: str = None, code: int | None = None):
        """Initializes the RAGFlowError with an optional message and code.

        :param message: (str, optional): The error message. If empty or None, defaults to "RAGFlow error".
        :param code: (int, optional):    The error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "RAGFlow error")
        self.code = code
