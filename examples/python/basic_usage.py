"""Basic usage examples for hudy-sdk."""
import os
from datetime import date

from hudy import HudyClient


def main():
    # Initialize client
    api_key = os.getenv("HUDY_API_KEY", "hd_live_demo")
    client = HudyClient(api_key=api_key)

    try:
        # Example 1: Get all holidays for 2024
        print("=== Example 1: Get Holidays for 2024 ===")
        holidays = client.get_holidays(2024)
        print(f"Found {len(holidays)} holidays in 2024:")
        for h in holidays:
            print(f"  {h.date}: {h.name}")

        # Example 2: Check if today is a holiday
        print("\n=== Example 2: Check Today ===")
        today = date.today()
        is_today_holiday = client.is_holiday(today)
        print(f"Is today a holiday? {'Yes' if is_today_holiday else 'No'}")

        # Example 3: Get holidays in a date range
        print("\n=== Example 3: Holidays in Q1 2024 ===")
        q1_holidays = client.get_holidays_by_range(date(2024, 1, 1), date(2024, 3, 31))
        print(f"Q1 2024 holidays: {len(q1_holidays)}")

        # Example 4: Count business days
        print("\n=== Example 4: Business Days in 2024 ===")
        business_days = client.get_business_days(date(2024, 1, 1), date(2024, 12, 31))
        print(f"Total business days in 2024: {business_days}")

        # Example 5: Get next business day
        print("\n=== Example 5: Next Business Day ===")
        next_business_day = client.get_next_business_day(date(2024, 1, 1))
        print(f"Next business day after 2024-01-01: {next_business_day}")

        # Example 6: Add business days
        print("\n=== Example 6: Add Business Days ===")
        future_date = client.add_business_days(date(2024, 1, 1), 10)
        print(f"10 business days after 2024-01-01: {future_date}")

        # Example 7: Cache statistics
        print("\n=== Example 7: Cache Statistics ===")
        stats = client.get_cache_stats()
        print(f"Cache hits: {stats.hits}, misses: {stats.misses}, size: {stats.size}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
