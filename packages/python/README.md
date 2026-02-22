# hudy-sdk

Official Python SDK for the Hudy Korean Public Holiday API.

[![PyPI version](https://badge.fury.io/py/hudy-sdk.svg)](https://badge.fury.io/py/hudy-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Smart Caching** - Intelligent year-based TTL for optimal performance
📅 **Business Day Calculations** - Count business days, skip weekends and holidays
🔒 **Type Safety** - Full type hints with Pydantic models
⚡ **Auto Retry** - Exponential backoff for failed requests
🎯 **Simple API** - Easy-to-use Pythonic interface

## Installation

```bash
pip install hudy-sdk
```

## Quick Start

```python
from hudy import HudyClient
from datetime import date

# Initialize client
client = HudyClient(api_key="hd_live_your_api_key_here")

# Get all holidays for 2024
holidays = client.get_holidays(2024)
for h in holidays:
    print(f"{h.date} ({h.day_of_week}): {h.name}")
    print(f"  Type: {h.type}, Public: {h.is_public}")

# Check if a date is a holiday
is_holiday = client.is_holiday(date(2024, 1, 1))
print(is_holiday)  # True

# Get business days between two dates
business_days = client.get_business_days(date(2024, 1, 1), date(2024, 12, 31))
print(f"Business days in 2024: {business_days}")

# Use as context manager
with HudyClient(api_key="hd_live_your_key") as client:
    holidays = client.get_holidays(2024)
```

## API Reference

### Constructor

```python
HudyClient(
    api_key: str,
    base_url: str = "https://api.hudy.co.kr",
    timeout: float = 10.0,
    cache: Optional[dict] = None,
    retry: Optional[dict] = None
)
```

**Parameters:**
- `api_key` (required): Your API key starting with `hd_live_`
- `base_url` (optional): API base URL
- `timeout` (optional): Request timeout in seconds (default: 10.0)
- `cache` (optional): Cache configuration dict
  - `enabled` (bool): Enable/disable caching (default: True)
  - `ttl` (int): Custom TTL in seconds (default: auto-calculated)
- `retry` (optional): Retry configuration dict
  - `enabled` (bool): Enable/disable retry (default: True)
  - `max_retries` (int): Maximum retry attempts (default: 3)
  - `initial_delay` (float): Initial delay in seconds (default: 1.0)
  - `max_delay` (float): Maximum delay in seconds (default: 10.0)
  - `backoff_factor` (float): Backoff multiplier (default: 2.0)

### Methods

#### get_holidays(year: int) -> List[Holiday]

Get all holidays for a specific year.

```python
holidays = client.get_holidays(2024)
```

#### get_holidays_by_range(from_date: date, to_date: date) -> List[Holiday]

Get holidays within a date range (inclusive).

**Note:** The backend API only supports fetching by year, so this method fetches full year(s) and filters the results client-side. For optimal performance with caching, prefer using year-based queries when possible.

```python
holidays = client.get_holidays_by_range(date(2024, 1, 1), date(2024, 3, 31))
```

#### is_holiday(check_date: date) -> bool

Check if a specific date is a holiday.

```python
is_holiday = client.is_holiday(date(2024, 1, 1))
```

#### get_business_days(from_date: date, to_date: date) -> int

Count business days between two dates.

```python
count = client.get_business_days(date(2024, 1, 1), date(2024, 12, 31))
```

#### get_next_business_day(from_date: date) -> date

Get the next business day after a given date.

```python
next_day = client.get_next_business_day(date(2024, 1, 1))
```

#### add_business_days(from_date: date, days: int) -> date

Add N business days to a date.

```python
future_date = client.add_business_days(date(2024, 1, 1), 10)
```

#### is_business_day(check_date: date) -> bool

Check if a date is a business day.

```python
is_business = client.is_business_day(date(2024, 1, 2))
```

#### get_cache_stats() -> CacheStats

Get cache statistics.

```python
stats = client.get_cache_stats()
print(f"Hits: {stats.hits}, Misses: {stats.misses}")
```

#### clear_cache() -> None

Clear all cached data.

```python
client.clear_cache()
```

## Types

### Holiday

```python
class Holiday:
    id: str
    name: str
    date: str                # YYYY-MM-DD format
    year: int
    month: int
    day: int
    day_of_week: str         # e.g., "Monday", "Tuesday"
    type: Literal['public', 'custom']

    # Computed convenience properties
    @property
    def is_public(self) -> bool:  # type == 'public'

    @property
    def is_custom(self) -> bool:  # type == 'custom'
```

## Error Handling

```python
from hudy import HudyClient, HudyError, ErrorCode

try:
    holidays = client.get_holidays(2024)
except HudyError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Status: {e.status_code}")
    print(f"Retryable: {e.retryable}")
```

**Error Codes:**
- `NETWORK_ERROR` - Network connectivity issue
- `TIMEOUT` - Request timeout
- `UNAUTHORIZED` - Invalid API key (401)
- `FORBIDDEN` - Access forbidden (403)
- `NOT_FOUND` - Resource not found (404)
- `RATE_LIMITED` - Rate limit exceeded (429)
- `BAD_REQUEST` - Invalid request (400)
- `INTERNAL_ERROR` - Server error (5xx)
- `INVALID_RESPONSE` - Malformed API response

## Advanced Usage

### Custom Configuration

```python
client = HudyClient(
    api_key="hd_live_your_key",
    base_url="https://custom.api.com",
    timeout=5.0,
    cache={"enabled": True, "ttl": 3600},
    retry={"enabled": True, "max_retries": 5}
)
```

### Disable Caching

```python
client = HudyClient(
    api_key="hd_live_your_key",
    cache={"enabled": False}
)
```

### Business Day Utilities

For offline calculation:

```python
from hudy import BusinessDayCalculator
from datetime import date

# Fetch holidays once
holidays = client.get_holidays(2024)

# Create calculator
calculator = BusinessDayCalculator(holidays)

# Use calculator (no API calls)
is_business = calculator.is_business_day(date(2024, 1, 2))
count = calculator.count_business_days(date(2024, 1, 1), date(2024, 12, 31))
next_day = calculator.get_next_business_day(date(2024, 1, 1))
```

## License

MIT

## Links

- [API Documentation](https://www.hudy.co.kr/#docs)
- [GitHub Repository](https://github.com/hudy-team/hudy_sdk)
- [Report Issues](https://github.com/hudy-team/hudy_sdk/issues)
