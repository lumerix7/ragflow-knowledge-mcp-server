"""exceptions.py"""


class ToolError(Exception):
    """
    Base exception for all tool-related errors.

    This class extends the standard Exception class and adds a code attribute to represent HTTP-like status codes.

    Properties:
        code (int | None): An optional error code, typically an HTTP status code.
    """
    code: int | None = None

    def __init__(self, message: str = None, code: int | None = None):
        """Initializes the ToolError with an optional message and code.

        Args:
            :param message: (str, optional):     The error message. If empty or None, defaults to "Tool error".
            :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Tool error")
        self.code = code

    def __str__(self) -> str:
        """Returns a string representation of the error, including the code if present.

        Returns:
            str: The error message, optionally with code information.
        """
        s = super().__str__()

        return f"{s} (code: {self.code})" if self.code else s


class ToolExecutionError(ToolError):
    """Exception class for errors that occur during tool execution."""

    def __init__(self, message: str = None, code: int | None = 500):
        """Initializes the ToolExecutionError with an optional message and code.

        :param message: (str, optional):     The error message. If empty or None, defaults to "Tool execution error".
        :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Tool execution error", code)


class ToolNotFoundError(ToolExecutionError):
    """Exception class for errors that occur when a tool is not found."""

    def __init__(self, message: str = None, code: int | None = 404):
        """Initializes the ToolNotFoundError with an optional message and code.

        :param message: (str, optional):     The error message. If empty or None, defaults to "Tool not found".
        :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Tool not found", code)


class InvalidToolArgumentError(ToolExecutionError):
    """Exception class for errors that occur when an invalid tool argument is provided."""

    def __init__(self, message: str = None, code: int | None = 400):
        """Initializes the InvalidToolArgumentError with an optional message and code.

        :param message: (str, optional):     The error message. If empty or None, defaults to "Invalid tool argument".
        :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Invalid tool argument", code)


class ToolAPIError(ToolExecutionError):
    """Exception class for errors that occur when a tool API call fails."""

    def __init__(self, message: str = None, code: int | None = None):
        """Initializes the ToolAPIError with an optional message and code.

        :param message: (str, optional):     The error message. If empty or None, defaults to "Tool API error".
        :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Tool API error", code)


class DataError(ToolExecutionError):
    """Exception class for errors related to data processing."""

    def __init__(self, message: str = None, code: int | None = None):
        """Initializes the DataError with an optional message and code.

        :param message: (str, optional):     The error message. If empty or None, defaults to "Data error".
        :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Data error", code)


class BizError(ToolExecutionError):
    """Exception class for business logic errors."""

    def __init__(self, message: str = None, code: int | None = None):
        """Initializes the BizError with an optional message and code.

        :param message: (str, optional):     The error message. If empty or None, defaults to "Business error".
        :param code: (int | None, optional): An error code, typically an HTTP status code.
        """
        super().__init__(message if message and message.strip() else "Business error", code)
