"""Business day calculation tests."""
from datetime import date

from hudy.utils.business_days import BusinessDayCalculator

from .helpers import MOCK_HOLIDAYS_2024, create_mock_holiday


class TestBusinessDayCalculator:
    """Test suite for BusinessDayCalculator."""

    def test_is_business_day_weekday(self):
        """Test business day check for weekdays."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        monday = date(2024, 1, 8)  # Not a holiday
        assert calculator.is_business_day(monday) is True

    def test_is_business_day_saturday(self):
        """Test business day check for Saturday."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        saturday = date(2024, 1, 6)
        assert calculator.is_business_day(saturday) is False

    def test_is_business_day_sunday(self):
        """Test business day check for Sunday."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        sunday = date(2024, 1, 7)
        assert calculator.is_business_day(sunday) is False

    def test_is_business_day_holiday(self):
        """Test business day check for public holiday."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        new_year = date(2024, 1, 1)  # 신정
        assert calculator.is_business_day(new_year) is False

    def test_is_business_day_holiday_on_weekday(self):
        """Test business day check for holiday on weekday."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        samil = date(2024, 3, 1)  # 삼일절 (Friday)
        assert calculator.is_business_day(samil) is False

    def test_count_business_days_one_week(self):
        """Test counting business days in a week without holidays."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 8)  # Monday
        to_date = date(2024, 1, 12)  # Friday
        count = calculator.count_business_days(from_date, to_date)
        assert count == 5

    def test_count_business_days_exclude_weekends(self):
        """Test counting business days excludes weekends."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 8)  # Monday
        to_date = date(2024, 1, 14)  # Sunday (next week)
        count = calculator.count_business_days(from_date, to_date)
        assert count == 5  # Mon-Fri only

    def test_count_business_days_exclude_holidays(self):
        """Test counting business days excludes holidays."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 2, 9)  # Friday (설날 연휴)
        to_date = date(2024, 2, 14)  # Wednesday
        # 2024-02-09 (Fri, holiday), 2024-02-10 (Sat, holiday), 2024-02-11 (Sun, holiday)
        # 2024-02-12 (Mon), 2024-02-13 (Tue), 2024-02-14 (Wed)
        count = calculator.count_business_days(from_date, to_date)
        assert count == 3  # Only Mon, Tue, Wed are business days

    def test_count_business_days_single_day_business(self):
        """Test counting single day (business day)."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        check_date = date(2024, 1, 8)  # Monday
        count = calculator.count_business_days(check_date, check_date)
        assert count == 1

    def test_count_business_days_single_day_weekend(self):
        """Test counting single day (weekend)."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        check_date = date(2024, 1, 6)  # Saturday
        count = calculator.count_business_days(check_date, check_date)
        assert count == 0

    def test_count_business_days_single_day_holiday(self):
        """Test counting single day (holiday)."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        check_date = date(2024, 1, 1)  # 신정
        count = calculator.count_business_days(check_date, check_date)
        assert count == 0

    def test_count_business_days_across_months(self):
        """Test counting business days across months."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 29)  # Monday
        to_date = date(2024, 2, 2)  # Friday
        # Jan 29 (Mon), 30 (Tue), 31 (Wed), Feb 1 (Thu), 2 (Fri)
        count = calculator.count_business_days(from_date, to_date)
        assert count == 5

    def test_count_business_days_long_range(self):
        """Test counting business days over long range."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 1)
        to_date = date(2024, 12, 31)
        count = calculator.count_business_days(from_date, to_date)

        # 2024 is a leap year (366 days)
        # Approximate: 52 weeks = 104 weekend days, 17 public holidays
        # ~245 business days (varies based on holiday positions)
        assert 240 < count < 250

    def test_get_next_business_day_friday_to_monday(self):
        """Test next business day from Friday."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        friday = date(2024, 1, 5)
        next_day = calculator.get_next_business_day(friday)
        assert next_day == date(2024, 1, 8)  # Monday

    def test_get_next_business_day_skip_weekend(self):
        """Test next business day skips weekend."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        saturday = date(2024, 1, 6)
        next_day = calculator.get_next_business_day(saturday)
        assert next_day == date(2024, 1, 8)  # Monday

    def test_get_next_business_day_skip_holiday(self):
        """Test next business day skips holiday."""
        holidays = [create_mock_holiday("2024-01-01", "신정")]
        calculator = BusinessDayCalculator(holidays)
        before_new_year = date(2023, 12, 29)  # Friday
        next_day = calculator.get_next_business_day(before_new_year)
        assert next_day == date(2024, 1, 2)  # Tuesday

    def test_get_next_business_day_skip_consecutive_holidays(self):
        """Test next business day skips consecutive holidays."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        before_chuseok = date(2024, 9, 13)  # Friday
        # 2024-09-16 (Mon, holiday), 2024-09-17 (Tue, holiday), 2024-09-18 (Wed, holiday)
        next_day = calculator.get_next_business_day(before_chuseok)
        assert next_day == date(2024, 9, 19)  # Thursday

    def test_get_next_business_day_from_business_day(self):
        """Test next business day from business day."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        monday = date(2024, 1, 8)
        next_day = calculator.get_next_business_day(monday)
        assert next_day == date(2024, 1, 9)  # Tuesday

    def test_add_business_days_positive(self):
        """Test adding positive business days."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 8)  # Monday
        result = calculator.add_business_days(from_date, 5)
        assert result == date(2024, 1, 15)  # Next Monday

    def test_add_business_days_zero(self):
        """Test adding zero business days."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 8)
        result = calculator.add_business_days(from_date, 0)
        assert result == from_date

    def test_add_business_days_negative(self):
        """Test subtracting business days."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 15)  # Monday
        result = calculator.add_business_days(from_date, -5)
        assert result == date(2024, 1, 8)  # Previous Monday

    def test_add_business_days_skip_weekend(self):
        """Test adding business days skips weekend."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        friday = date(2024, 1, 5)
        result = calculator.add_business_days(friday, 1)
        assert result == date(2024, 1, 8)  # Monday

    def test_add_business_days_skip_holiday(self):
        """Test adding business days skips holiday."""
        holidays = [
            create_mock_holiday("2024-01-01", "신정"),
            create_mock_holiday("2024-01-02", "대체공휴일"),
        ]
        calculator = BusinessDayCalculator(holidays)
        before_new_year = date(2023, 12, 29)  # Friday
        result = calculator.add_business_days(before_new_year, 1)
        assert result == date(2024, 1, 3)  # Wednesday

    def test_add_business_days_multiple_weeks(self):
        """Test adding days across multiple weeks."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 8)  # Monday
        result = calculator.add_business_days(from_date, 10)
        # 10 business days = 2 full weeks
        assert result == date(2024, 1, 22)  # Monday

    def test_add_business_days_subtract_multiple_weeks(self):
        """Test subtracting days across multiple weeks."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 1, 22)  # Monday
        result = calculator.add_business_days(from_date, -10)
        assert result == date(2024, 1, 8)  # Monday

    def test_add_business_days_from_weekend(self):
        """Test adding business days starting from weekend."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        saturday = date(2024, 1, 6)
        result = calculator.add_business_days(saturday, 1)
        assert result == date(2024, 1, 8)  # Tuesday (skip Sat, Sun, Mon becomes day 1)

    def test_add_business_days_complex_holidays(self):
        """Test adding days with complex holiday arrangement."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        from_date = date(2024, 2, 8)  # Thursday before 설날
        # 2024-02-09 (Fri, holiday), 2024-02-10 (Sat, holiday), 2024-02-11 (Sun, holiday)
        # Next business day is 2024-02-12 (Mon)
        result = calculator.add_business_days(from_date, 1)
        assert result == date(2024, 2, 12)  # Monday


class TestBusinessDayCalculatorEdgeCases:
    """Test edge cases for BusinessDayCalculator."""

    def test_empty_holiday_list(self):
        """Test calculator with no holidays."""
        calculator = BusinessDayCalculator([])
        from_date = date(2024, 1, 8)  # Monday
        to_date = date(2024, 1, 12)  # Friday
        count = calculator.count_business_days(from_date, to_date)
        assert count == 5

    def test_no_holidays_means_weekdays_are_business_days(self):
        """Test that without holidays, all weekdays are business days."""
        calculator = BusinessDayCalculator([])
        monday = date(2024, 1, 1)  # Monday (would be holiday normally)
        assert calculator.is_business_day(monday) is True

    def test_year_boundaries(self):
        """Test business day calculation across year boundaries."""
        holidays = [
            create_mock_holiday("2023-12-25", "Christmas"),
            create_mock_holiday("2024-01-01", "신정"),
        ]
        calculator = BusinessDayCalculator(holidays)

        from_date = date(2023, 12, 22)  # Friday
        to_date = date(2024, 1, 5)  # Friday
        count = calculator.count_business_days(from_date, to_date)

        # Should count business days across the year boundary
        assert count > 5

    def test_same_day_twice(self):
        """Test counting same day twice."""
        calculator = BusinessDayCalculator(MOCK_HOLIDAYS_2024)
        monday = date(2024, 1, 8)
        count = calculator.count_business_days(monday, monday)
        assert count == 1
