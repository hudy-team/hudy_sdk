"""Hudy Korean Public Holiday API SDK."""

__version__ = "0.1.0"

from .client import HudyClient
from .errors import ErrorCode, HudyError
from .types import (
    CacheOptions,
    CacheStats,
    ClientOptions,
    Holiday,
    RetryOptions,
)
from .utils import BusinessDayCalculator
from .utils.date import (
    add_days,
    days_between,
    format_date,
    is_same_day,
    is_weekend,
    parse_date,
)

__all__ = [
    "HudyClient",
    "HudyError",
    "ErrorCode",
    "Holiday",
    "ClientOptions",
    "CacheOptions",
    "RetryOptions",
    "CacheStats",
    "BusinessDayCalculator",
    "format_date",
    "parse_date",
    "is_weekend",
    "add_days",
    "is_same_day",
    "days_between",
    "__version__",
]
