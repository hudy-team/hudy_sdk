"""Date utility functions."""

from datetime import date, timedelta


def format_date(d: date) -> str:
    """Format a date to YYYY-MM-DD string."""
    return d.strftime("%Y-%m-%d")


def parse_date(date_str: str) -> date:
    """Parse YYYY-MM-DD string to date object."""
    year, month, day = map(int, date_str.split("-"))
    return date(year, month, day)


def is_weekend(d: date) -> bool:
    """Check if a date is a weekend (Saturday or Sunday)."""
    return d.weekday() in (5, 6)  # 5=Saturday, 6=Sunday


def add_days(d: date, days: int) -> date:
    """Add days to a date."""
    return d + timedelta(days=days)


def is_same_day(date1: date, date2: date) -> bool:
    """Check if two dates are the same day."""
    return date1 == date2


def days_between(from_date: date, to_date: date) -> int:
    """Get the number of days between two dates (inclusive)."""
    delta = to_date - from_date
    return delta.days + 1  # +1 for inclusive
