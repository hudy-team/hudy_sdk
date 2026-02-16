"""Hudy API client."""
import time
from datetime import date, timedelta
from typing import List, Optional

import httpx
from pydantic import ValidationError

from .cache import SmartCache
from .errors import HudyError
from .types import (
    ApiErrorResponse,
    ApiSuccessResponse,
    CacheStats,
    ClientOptions,
    Holiday,
)
from .utils.business_days import BusinessDayCalculator


class HudyClient:
    """Hudy Korean Public Holiday API client."""

    def __init__(self, api_key: str, **kwargs: any) -> None:
        """
        Initialize Hudy client.

        Args:
            api_key: API key (must start with hd_live_)
            base_url: API base URL (default: https://api.hudy.kr)
            timeout: Request timeout in seconds (default: 10.0)
            cache: Cache options dict or CacheOptions instance
            retry: Retry options dict or RetryOptions instance
        """
        # Validate and store options
        self._options = ClientOptions(api_key=api_key, **kwargs)

        # HTTP client
        self._client = httpx.Client(
            timeout=self._options.timeout,
            headers={
                "x-api-key": self._options.api_key,
                "Content-Type": "application/json",
            },
        )

        # Initialize cache
        cache_enabled = self._options.cache.enabled
        custom_ttl = self._options.cache.ttl
        self._cache: Optional[SmartCache] = SmartCache(custom_ttl=custom_ttl) if cache_enabled else None

    def __enter__(self) -> "HudyClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: any, exc_val: any, exc_tb: any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def get_holidays(self, year: int) -> List[Holiday]:
        """
        Get all holidays for a specific year.

        Args:
            year: Year (1900-2100)

        Returns:
            List of holidays

        Raises:
            ValueError: If year is invalid
            HudyError: If API request fails
        """
        if not isinstance(year, int) or not (1900 <= year <= 2100):
            raise ValueError("Year must be an integer between 1900 and 2100")

        # Check cache first
        if self._cache:
            cached = self._cache.get(year)
            if cached:
                return cached

        # Fetch from API
        url = f"{self._options.base_url}/v1/holidays?year={year}"
        holidays = self._request(url)

        # Store in cache
        if self._cache:
            self._cache.set(year, holidays)

        return holidays

    def get_holidays_by_range(self, from_date: date, to_date: date) -> List[Holiday]:
        """
        Get holidays within a date range.

        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)

        Returns:
            List of holidays

        Raises:
            ValueError: If date range is invalid
            HudyError: If API request fails
        """
        if from_date > to_date:
            raise ValueError("from_date must be before or equal to to_date")

        from_year = from_date.year
        to_year = to_date.year
        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")

        # If single year, fetch that year and filter
        if from_year == to_year:
            holidays = self.get_holidays(from_year)
            return [h for h in holidays if from_str <= h.date <= to_str]

        # Multi-year: fetch all years and filter
        all_holidays: List[Holiday] = []
        for year in range(from_year, to_year + 1):
            year_holidays = self.get_holidays(year)
            all_holidays.extend(year_holidays)

        return [h for h in all_holidays if from_str <= h.date <= to_str]

    def is_holiday(self, check_date: date) -> bool:
        """
        Check if a specific date is a holiday.

        Args:
            check_date: Date to check

        Returns:
            True if the date is a holiday

        Raises:
            HudyError: If API request fails
        """
        year = check_date.year
        holidays = self.get_holidays(year)
        date_str = check_date.strftime("%Y-%m-%d")
        return any(h.date == date_str for h in holidays)

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._cache.get_stats() if self._cache else CacheStats()

    def clear_cache(self) -> None:
        """Clear all cached data."""
        if self._cache:
            self._cache.clear()

    def prune_cache(self) -> int:
        """Remove expired cache entries."""
        return self._cache.prune() if self._cache else 0

    def get_business_days(self, from_date: date, to_date: date) -> int:
        """
        Get business days between two dates (inclusive).

        Args:
            from_date: Start date
            to_date: End date

        Returns:
            Number of business days

        Raises:
            ValueError: If from_date > to_date
            HudyError: If API request fails
        """
        if from_date > to_date:
            raise ValueError("from_date must be before or equal to to_date")

        holidays = self.get_holidays_by_range(from_date, to_date)
        calculator = BusinessDayCalculator(holidays)
        return calculator.count_business_days(from_date, to_date)

    def get_next_business_day(self, from_date: date) -> date:
        """
        Get the next business day after a given date.

        Args:
            from_date: Starting date

        Returns:
            Next business day

        Raises:
            HudyError: If API request fails
        """
        # Fetch holidays for the year and next year
        year = from_date.year
        holidays = list(self.get_holidays(year))  # Create copy to avoid mutation

        # Check if we need next year's holidays
        check_date = from_date
        for _ in range(366):  # Max iterations
            check_date = check_date + timedelta(days=1)

            if check_date.year > year:
                next_year_holidays = self.get_holidays(year + 1)
                holidays.extend(next_year_holidays)
                break

        calculator = BusinessDayCalculator(holidays)
        return calculator.get_next_business_day(from_date)

    def add_business_days(self, from_date: date, days: int) -> date:
        """
        Add N business days to a date.

        Args:
            from_date: Starting date
            days: Number of business days to add (can be negative)

        Returns:
            Date that is N business days from from_date

        Raises:
            HudyError: If API request fails
        """
        if days == 0:
            return from_date

        # Estimate the date range needed
        estimated_days = int(abs(days) * 1.4) + 14  # Buffer for holidays
        direction = 1 if days > 0 else -1

        estimated_end = from_date + timedelta(days=estimated_days * direction)

        # Fetch holidays for the range
        start_date = from_date if direction > 0 else estimated_end
        end_date = estimated_end if direction > 0 else from_date
        holidays = self.get_holidays_by_range(start_date, end_date)

        calculator = BusinessDayCalculator(holidays)
        return calculator.add_business_days(from_date, days)

    def is_business_day(self, check_date: date) -> bool:
        """
        Check if a date is a business day.

        Args:
            check_date: Date to check

        Returns:
            True if the date is a business day

        Raises:
            HudyError: If API request fails
        """
        year = check_date.year
        holidays = self.get_holidays(year)
        calculator = BusinessDayCalculator(holidays)
        return calculator.is_business_day(check_date)

    # Private methods

    def _request(self, url: str) -> List[Holiday]:
        """Execute HTTP request with retry logic."""
        if self._options.retry.enabled:
            return self._request_with_retry(url)
        else:
            return self._execute_request(url)

    def _request_with_retry(self, url: str) -> List[Holiday]:
        """Execute request with exponential backoff retry."""
        last_error: Optional[HudyError] = None
        delay = self._options.retry.initial_delay

        for attempt in range(self._options.retry.max_retries + 1):
            try:
                return self._execute_request(url)
            except HudyError as e:
                if not e.retryable:
                    raise

                last_error = e

                if attempt < self._options.retry.max_retries:
                    time.sleep(delay)
                    delay = min(
                        delay * self._options.retry.backoff_factor,
                        self._options.retry.max_delay,
                    )

        raise last_error  # type: ignore

    def _execute_request(self, url: str) -> List[Holiday]:
        """Execute a single HTTP request."""
        try:
            response = self._client.get(url)

            # Parse JSON response
            try:
                json_data = response.json()
            except Exception as e:
                raise HudyError.invalid_response(f"Invalid JSON response: {e}")

            # Try to parse as success response
            try:
                success_resp = ApiSuccessResponse.model_validate(json_data)
                return success_resp.data
            except ValidationError:
                pass

            # Try to parse as error response
            try:
                error_resp = ApiErrorResponse.model_validate(json_data)
                raise HudyError.from_response(
                    response.status_code,
                    error_resp.error.get("message", "Unknown error"),
                )
            except ValidationError:
                pass

            # Neither format matched
            if not response.is_success:
                raise HudyError.from_response(
                    response.status_code,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                )

            raise HudyError.invalid_response("Response does not match expected format")

        except httpx.TimeoutException:
            raise HudyError.timeout(f"Request timeout after {self._options.timeout}s")
        except httpx.HTTPError as e:
            raise HudyError.network_error(str(e))
        except HudyError:
            raise
        except Exception as e:
            raise HudyError.network_error(f"Unexpected error: {e}")
