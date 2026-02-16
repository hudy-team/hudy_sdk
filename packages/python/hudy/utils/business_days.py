"""Business day calculation utilities."""

from datetime import date
from typing import List, Set

from ..types import Holiday
from .date import add_days, format_date, is_weekend


class BusinessDayCalculator:
    """Business day calculator with holiday awareness."""

    def __init__(self, holidays: List[Holiday]):
        """
        Initialize calculator with holidays.

        Args:
            holidays: List of holidays to consider
        """
        self._holiday_set: Set[str] = {h.date for h in holidays}

    def is_business_day(self, d: date) -> bool:
        """
        Check if a date is a business day.

        Args:
            d: Date to check

        Returns:
            True if the date is a business day (not weekend or holiday)
        """
        # Weekend check
        if is_weekend(d):
            return False

        # Holiday check
        date_str = format_date(d)
        return date_str not in self._holiday_set

    def count_business_days(self, from_date: date, to_date: date) -> int:
        """
        Count business days between two dates (inclusive).

        Args:
            from_date: Start date
            to_date: End date

        Returns:
            Number of business days

        Raises:
            ValueError: If from_date > to_date
        """
        if from_date > to_date:
            raise ValueError("from_date must be before or equal to to_date")

        count = 0
        current = from_date

        while current <= to_date:
            if self.is_business_day(current):
                count += 1
            current = add_days(current, 1)

        return count

    def get_next_business_day(self, from_date: date) -> date:
        """
        Get the next business day after the given date.

        Args:
            from_date: Starting date

        Returns:
            Next business day after from_date
        """
        current = add_days(from_date, 1)

        while not self.is_business_day(current):
            current = add_days(current, 1)

        return current

    def get_previous_business_day(self, from_date: date) -> date:
        """
        Get the previous business day before the given date.

        Args:
            from_date: Starting date

        Returns:
            Previous business day before from_date
        """
        current = add_days(from_date, -1)

        while not self.is_business_day(current):
            current = add_days(current, -1)

        return current

    def add_business_days(self, from_date: date, days: int) -> date:
        """
        Add N business days to a date.

        Args:
            from_date: Starting date
            days: Number of business days to add (can be negative)

        Returns:
            Date that is N business days from from_date
        """
        if days == 0:
            return from_date

        direction = 1 if days > 0 else -1
        remaining = abs(days)
        current = from_date
        added = 0

        while added < remaining:
            current = add_days(current, direction)
            if self.is_business_day(current):
                added += 1

        return current

    def get_business_days_in_range(self, from_date: date, to_date: date) -> List[date]:
        """
        Get all business days in a range (inclusive).

        Args:
            from_date: Start date
            to_date: End date

        Returns:
            List of business days in the range

        Raises:
            ValueError: If from_date > to_date
        """
        if from_date > to_date:
            raise ValueError("from_date must be before or equal to to_date")

        business_days: List[date] = []
        current = from_date

        while current <= to_date:
            if self.is_business_day(current):
                business_days.append(current)
            current = add_days(current, 1)

        return business_days
