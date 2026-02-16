"""HudyClient tests."""
from datetime import date
from unittest.mock import Mock, patch

import httpx
import pytest

from hudy.client import HudyClient
from hudy.errors import HudyError

from .helpers import (
    MOCK_HOLIDAYS_2024,
    MOCK_HOLIDAYS_2024_DATA,
    create_error_response,
    create_success_response,
)


class TestHudyClient:
    """Test suite for HudyClient."""

    def test_constructor_valid_api_key(self):
        """Test client creation with valid API key."""
        client = HudyClient(api_key="hd_live_test123")
        assert client is not None

    def test_constructor_missing_api_key(self):
        """Test error when API key is missing."""
        with pytest.raises(ValueError, match="API key must start with hd_live_"):
            HudyClient(api_key="")

    def test_constructor_invalid_api_key_prefix(self):
        """Test error when API key has wrong prefix."""
        with pytest.raises(ValueError, match="API key must start with hd_live_"):
            HudyClient(api_key="invalid_key")

    def test_constructor_default_options(self):
        """Test default configuration options."""
        client = HudyClient(api_key="hd_live_test123")
        assert client._options.base_url == "https://api.hudy.co.kr"
        assert client._options.timeout == 10.0
        assert client._options.cache.enabled is True
        assert client._options.retry.enabled is True

    def test_constructor_custom_options(self):
        """Test custom configuration options."""
        client = HudyClient(
            api_key="hd_live_test123",
            base_url="https://custom.api.com",
            timeout=5.0,
        )
        assert client._options.base_url == "https://custom.api.com"
        assert client._options.timeout == 5.0

    def test_context_manager(self):
        """Test client as context manager."""
        with HudyClient(api_key="hd_live_test123") as client:
            assert client is not None
        # Client should be closed after context

    @patch("httpx.Client.get")
    def test_get_holidays_success(self, mock_get):
        """Test successful holiday fetch."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})
        holidays = client.get_holidays(2024)

        assert len(holidays) == len(MOCK_HOLIDAYS_2024_DATA)
        assert holidays[0].name == "신정"
        assert holidays[0].date == "2024-01-01"
        assert holidays[0].type == "public"

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "year=2024" in call_args[0][0]

    @patch("httpx.Client.get")
    def test_get_holidays_invalid_year_low(self, mock_get):
        """Test error for year too low."""
        client = HudyClient(api_key="hd_live_test123")

        with pytest.raises(ValueError, match="Year must be an integer between 1900 and 2100"):
            client.get_holidays(1899)

    @patch("httpx.Client.get")
    def test_get_holidays_invalid_year_high(self, mock_get):
        """Test error for year too high."""
        client = HudyClient(api_key="hd_live_test123")

        with pytest.raises(ValueError, match="Year must be an integer between 1900 and 2100"):
            client.get_holidays(2101)

    @patch("httpx.Client.get")
    def test_get_holidays_invalid_year_non_integer(self, mock_get):
        """Test error for non-integer year."""
        client = HudyClient(api_key="hd_live_test123")

        with pytest.raises(ValueError, match="Year must be an integer between 1900 and 2100"):
            client.get_holidays(2024.5)

    @patch("httpx.Client.get")
    def test_get_holidays_api_error(self, mock_get):
        """Test handling of API error response."""
        mock_response = Mock()
        mock_response.json.return_value = create_error_response("Unauthorized")
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})

        with pytest.raises(HudyError) as exc_info:
            client.get_holidays(2024)

        assert exc_info.value.code == "UNAUTHORIZED"

    @patch("httpx.Client.get")
    def test_get_holidays_network_error(self, mock_get):
        """Test handling of network error."""
        mock_get.side_effect = httpx.NetworkError("Network failed")

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})

        with pytest.raises(HudyError) as exc_info:
            client.get_holidays(2024)

        assert exc_info.value.code == "NETWORK_ERROR"

    @patch("httpx.Client.get")
    def test_get_holidays_timeout(self, mock_get):
        """Test handling of timeout."""
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        client = HudyClient(api_key="hd_live_test123", timeout=0.1, retry={"enabled": False})

        with pytest.raises(HudyError) as exc_info:
            client.get_holidays(2024)

        assert exc_info.value.code == "TIMEOUT"

    @patch("httpx.Client.get")
    def test_get_holidays_by_range_single_year(self, mock_get):
        """Test getting holidays within a date range (single year)."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})
        from_date = date(2024, 2, 1)
        to_date = date(2024, 3, 31)

        holidays = client.get_holidays_by_range(from_date, to_date)

        # Should include Feb 9, 10, 11 (설날) and Mar 1 (삼일절)
        assert len(holidays) == 4
        assert holidays[0].date == "2024-02-09"
        assert holidays[3].date == "2024-03-01"

    @patch("httpx.Client.get")
    def test_get_holidays_by_range_multiple_years(self, mock_get):
        """Test getting holidays across multiple years."""
        mock_2024 = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_2025 = create_success_response([
            {
                "id": "hol_2025_0101",
                "name": "신정",
                "date": "2025-01-01",
                "year": 2025,
                "month": 1,
                "day": 1,
                "day_of_week": "Wednesday",
                "type": "public",
            }
        ])

        mock_response_2024 = Mock()
        mock_response_2024.json.return_value = mock_2024
        mock_response_2024.is_success = True

        mock_response_2025 = Mock()
        mock_response_2025.json.return_value = mock_2025
        mock_response_2025.is_success = True

        mock_get.side_effect = [mock_response_2024, mock_response_2025]

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})
        from_date = date(2024, 12, 1)
        to_date = date(2025, 1, 31)

        holidays = client.get_holidays_by_range(from_date, to_date)

        # Should include 2024-12-25 (크리스마스) and 2025-01-01 (신정)
        assert len(holidays) == 2
        assert holidays[0].date == "2024-12-25"
        assert holidays[1].date == "2025-01-01"

    @patch("httpx.Client.get")
    def test_get_holidays_by_range_invalid_range(self, mock_get):
        """Test error when from_date > to_date."""
        client = HudyClient(api_key="hd_live_test123")
        from_date = date(2024, 12, 31)
        to_date = date(2024, 1, 1)

        with pytest.raises(ValueError, match="from_date must be before or equal to to_date"):
            client.get_holidays_by_range(from_date, to_date)

    @patch("httpx.Client.get")
    def test_get_holidays_by_range_single_day(self, mock_get):
        """Test getting holidays for a single day."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})
        check_date = date(2024, 1, 1)

        holidays = client.get_holidays_by_range(check_date, check_date)

        assert len(holidays) == 1
        assert holidays[0].date == "2024-01-01"

    @patch("httpx.Client.get")
    def test_is_holiday_true(self, mock_get):
        """Test checking if a date is a holiday (true case)."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})
        result = client.is_holiday(date(2024, 1, 1))

        assert result is True

    @patch("httpx.Client.get")
    def test_is_holiday_false(self, mock_get):
        """Test checking if a date is a holiday (false case)."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": False}, retry={"enabled": False})
        result = client.is_holiday(date(2024, 1, 2))

        assert result is False


class TestHudyClientCache:
    """Test suite for caching functionality."""

    @patch("httpx.Client.get")
    def test_cache_stores_data(self, mock_get):
        """Test that cache stores data after first fetch."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": True}, retry={"enabled": False})

        # First call
        client.get_holidays(2024)
        assert mock_get.call_count == 1

        # Second call (should use cache)
        client.get_holidays(2024)
        assert mock_get.call_count == 1  # Still 1

    @patch("httpx.Client.get")
    def test_cache_stats(self, mock_get):
        """Test cache statistics tracking."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": True}, retry={"enabled": False})

        client.get_holidays(2024)  # Miss
        client.get_holidays(2024)  # Hit

        stats = client.get_cache_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.size == 1

    @patch("httpx.Client.get")
    def test_clear_cache(self, mock_get):
        """Test clearing cache."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": True}, retry={"enabled": False})

        client.get_holidays(2024)
        client.clear_cache()

        stats = client.get_cache_stats()
        assert stats.size == 0

    @patch("httpx.Client.get")
    def test_prune_cache(self, mock_get):
        """Test pruning expired cache entries."""
        mock_response = Mock()
        mock_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        mock_response.is_success = True
        mock_get.return_value = mock_response

        client = HudyClient(api_key="hd_live_test123", cache={"enabled": True}, retry={"enabled": False})

        client.get_holidays(2024)
        pruned = client.prune_cache()

        # No entries should be expired immediately
        assert pruned == 0


class TestHudyClientRetry:
    """Test suite for retry logic."""

    @patch("httpx.Client.get")
    def test_retry_on_retryable_error(self, mock_get):
        """Test retry on retryable errors."""
        error_response = Mock()
        error_response.json.return_value = create_error_response("Service Unavailable")
        error_response.status_code = 503
        error_response.is_success = False

        success_response = Mock()
        success_response.json.return_value = create_success_response(MOCK_HOLIDAYS_2024_DATA)
        success_response.is_success = True

        # Fail twice, succeed on third attempt
        mock_get.side_effect = [error_response, error_response, success_response]

        client = HudyClient(
            api_key="hd_live_test123",
            cache={"enabled": False},
            retry={"enabled": True, "max_retries": 2, "initial_delay": 0.01},
        )

        holidays = client.get_holidays(2024)
        assert len(holidays) == len(MOCK_HOLIDAYS_2024_DATA)
        assert mock_get.call_count == 3

    @patch("httpx.Client.get")
    def test_no_retry_on_non_retryable_error(self, mock_get):
        """Test no retry on non-retryable errors."""
        mock_response = Mock()
        mock_response.json.return_value = create_error_response("Unauthorized")
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_get.return_value = mock_response

        client = HudyClient(
            api_key="hd_live_test123",
            cache={"enabled": False},
            retry={"enabled": True, "max_retries": 2},
        )

        with pytest.raises(HudyError):
            client.get_holidays(2024)

        assert mock_get.call_count == 1

    @patch("httpx.Client.get")
    def test_max_retries_exceeded(self, mock_get):
        """Test failure after max retries."""
        mock_response = Mock()
        mock_response.json.return_value = create_error_response("Service Unavailable")
        mock_response.status_code = 503
        mock_response.is_success = False
        mock_get.return_value = mock_response

        client = HudyClient(
            api_key="hd_live_test123",
            cache={"enabled": False},
            retry={"enabled": True, "max_retries": 2, "initial_delay": 0.01},
        )

        with pytest.raises(HudyError):
            client.get_holidays(2024)

        assert mock_get.call_count == 3  # 1 initial + 2 retries
