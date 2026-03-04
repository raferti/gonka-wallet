class TransportError(Exception):
    """HTTP transport error with status code and message."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class TransactionNotFound(Exception):
    pass


class TransactionTimeout(Exception):
    pass
