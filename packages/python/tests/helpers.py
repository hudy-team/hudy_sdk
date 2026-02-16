"""Test helper utilities."""
from datetime import date
from typing import Any, Dict, List, Literal

from hudy.types import Holiday


def create_mock_holiday(
    date_str: str,
    name: str,
    holiday_type: Literal['public', 'custom'] = 'public'
) -> Holiday:
    """Create a mock holiday for testing."""
    year, month, day_num = map(int, date_str.split('-'))
    date_obj = date(year, month, day_num)
    day_of_week = date_obj.strftime('%A')

    return Holiday(
        id=f"holiday_{date_str}",
        name=name,
        date=date_str,
        year=year,
        month=month,
        day=day_num,
        day_of_week=day_of_week,
        type=holiday_type,
    )


# Mock holiday data for 2024 (raw dict format)
MOCK_HOLIDAYS_2024_DATA: List[Dict[str, Any]] = [
    {
        "id": "hol_2024_0101",
        "name": "신정",
        "date": "2024-01-01",
        "year": 2024,
        "month": 1,
        "day": 1,
        "day_of_week": "Monday",
        "type": "public",
    },
    {
        "id": "hol_2024_0209",
        "name": "설날 연휴",
        "date": "2024-02-09",
        "year": 2024,
        "month": 2,
        "day": 9,
        "day_of_week": "Friday",
        "type": "public",
    },
    {
        "id": "hol_2024_0210",
        "name": "설날",
        "date": "2024-02-10",
        "year": 2024,
        "month": 2,
        "day": 10,
        "day_of_week": "Saturday",
        "type": "public",
    },
    {
        "id": "hol_2024_0211",
        "name": "설날 연휴",
        "date": "2024-02-11",
        "year": 2024,
        "month": 2,
        "day": 11,
        "day_of_week": "Sunday",
        "type": "public",
    },
    {
        "id": "hol_2024_0301",
        "name": "삼일절",
        "date": "2024-03-01",
        "year": 2024,
        "month": 3,
        "day": 1,
        "day_of_week": "Friday",
        "type": "public",
    },
    {
        "id": "hol_2024_0410",
        "name": "제22대 국회의원 선거일",
        "date": "2024-04-10",
        "year": 2024,
        "month": 4,
        "day": 10,
        "day_of_week": "Wednesday",
        "type": "public",
    },
    {
        "id": "hol_2024_0505",
        "name": "어린이날",
        "date": "2024-05-05",
        "year": 2024,
        "month": 5,
        "day": 5,
        "day_of_week": "Sunday",
        "type": "public",
    },
    {
        "id": "hol_2024_0506",
        "name": "어린이날 대체공휴일",
        "date": "2024-05-06",
        "year": 2024,
        "month": 5,
        "day": 6,
        "day_of_week": "Monday",
        "type": "public",
    },
    {
        "id": "hol_2024_0515",
        "name": "석가탄신일",
        "date": "2024-05-15",
        "year": 2024,
        "month": 5,
        "day": 15,
        "day_of_week": "Wednesday",
        "type": "public",
    },
    {
        "id": "hol_2024_0606",
        "name": "현충일",
        "date": "2024-06-06",
        "year": 2024,
        "month": 6,
        "day": 6,
        "day_of_week": "Thursday",
        "type": "public",
    },
    {
        "id": "hol_2024_0815",
        "name": "광복절",
        "date": "2024-08-15",
        "year": 2024,
        "month": 8,
        "day": 15,
        "day_of_week": "Thursday",
        "type": "public",
    },
    {
        "id": "hol_2024_0916",
        "name": "추석 연휴",
        "date": "2024-09-16",
        "year": 2024,
        "month": 9,
        "day": 16,
        "day_of_week": "Monday",
        "type": "public",
    },
    {
        "id": "hol_2024_0917",
        "name": "추석",
        "date": "2024-09-17",
        "year": 2024,
        "month": 9,
        "day": 17,
        "day_of_week": "Tuesday",
        "type": "public",
    },
    {
        "id": "hol_2024_0918",
        "name": "추석 연휴",
        "date": "2024-09-18",
        "year": 2024,
        "month": 9,
        "day": 18,
        "day_of_week": "Wednesday",
        "type": "public",
    },
    {
        "id": "hol_2024_1003",
        "name": "개천절",
        "date": "2024-10-03",
        "year": 2024,
        "month": 10,
        "day": 3,
        "day_of_week": "Thursday",
        "type": "public",
    },
    {
        "id": "hol_2024_1009",
        "name": "한글날",
        "date": "2024-10-09",
        "year": 2024,
        "month": 10,
        "day": 9,
        "day_of_week": "Wednesday",
        "type": "public",
    },
    {
        "id": "hol_2024_1225",
        "name": "크리스마스",
        "date": "2024-12-25",
        "year": 2024,
        "month": 12,
        "day": 25,
        "day_of_week": "Wednesday",
        "type": "public",
    },
]

# Convert to Holiday objects
MOCK_HOLIDAYS_2024: List[Holiday] = [
    Holiday(**data) for data in MOCK_HOLIDAYS_2024_DATA
]


def create_success_response(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a successful API response envelope."""
    return {
        "result": True,
        "data": data,
    }


def create_error_response(message: str) -> Dict[str, Any]:
    """Create an error API response envelope."""
    return {
        "result": False,
        "error": {"message": message},
    }
