"""Error types for the Hudy SDK."""

from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    """Error codes for Hudy SDK errors."""

    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    BAD_REQUEST = "BAD_REQUEST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"


class HudyError(Exception):
    """Base exception for Hudy SDK errors."""

    def __init__(
        self,
        message: str,
        code: ErrorCode,
        status_code: Optional[int] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.retryable = retryable

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.code.value}] HTTP {self.status_code}: {self.message}"
        return f"[{self.code.value}] {self.message}"

    @classmethod
    def from_response(cls, status: int, message: str) -> "HudyError":
        """Create error from HTTP response."""
        if status == 401:
            return cls(message, ErrorCode.UNAUTHORIZED, status, False)
        elif status == 403:
            return cls(message, ErrorCode.FORBIDDEN, status, False)
        elif status == 404:
            return cls(message, ErrorCode.NOT_FOUND, status, False)
        elif status == 429:
            return cls(message, ErrorCode.RATE_LIMITED, status, True)
        elif status == 400:
            return cls(message, ErrorCode.BAD_REQUEST, status, False)
        else:
            return cls(
                message,
                ErrorCode.INTERNAL_ERROR,
                status,
                status >= 500,
            )

    @classmethod
    def network_error(cls, message: str) -> "HudyError":
        """Create network error."""
        return cls(message, ErrorCode.NETWORK_ERROR, retryable=True)

    @classmethod
    def timeout(cls, message: str) -> "HudyError":
        """Create timeout error."""
        return cls(message, ErrorCode.TIMEOUT, retryable=True)

    @classmethod
    def invalid_response(cls, message: str) -> "HudyError":
        """Create invalid response error."""
        return cls(message, ErrorCode.INVALID_RESPONSE, retryable=False)
