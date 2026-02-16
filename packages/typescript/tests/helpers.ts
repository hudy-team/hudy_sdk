/**
 * Test helper utilities
 */

import { Holiday } from '../src/types';

/**
 * Create a mock Holiday instance for testing
 */
export function createMockHoliday(
  date: string,
  name: string,
  type: 'public' | 'custom' = 'public'
): Holiday {
  const [yearStr, monthStr, dayStr] = date.split('-');
  const dateObj = new Date(date);
  const dayOfWeek = dateObj.toLocaleDateString('en-US', { weekday: 'long' });

  return new Holiday(
    `holiday_${date}`,
    name,
    date,
    parseInt(yearStr),
    parseInt(monthStr),
    parseInt(dayStr),
    dayOfWeek,
    type
  );
}

/**
 * Mock holidays for 2024
 */
export const mockHolidays2024Raw = [
  {
    id: 'hol_2024_0101',
    name: '신정',
    date: '2024-01-01',
    year: 2024,
    month: 1,
    day: 1,
    day_of_week: 'Monday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0209',
    name: '설날 연휴',
    date: '2024-02-09',
    year: 2024,
    month: 2,
    day: 9,
    day_of_week: 'Friday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0210',
    name: '설날',
    date: '2024-02-10',
    year: 2024,
    month: 2,
    day: 10,
    day_of_week: 'Saturday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0211',
    name: '설날 연휴',
    date: '2024-02-11',
    year: 2024,
    month: 2,
    day: 11,
    day_of_week: 'Sunday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0301',
    name: '삼일절',
    date: '2024-03-01',
    year: 2024,
    month: 3,
    day: 1,
    day_of_week: 'Friday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0410',
    name: '제22대 국회의원 선거일',
    date: '2024-04-10',
    year: 2024,
    month: 4,
    day: 10,
    day_of_week: 'Wednesday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0505',
    name: '어린이날',
    date: '2024-05-05',
    year: 2024,
    month: 5,
    day: 5,
    day_of_week: 'Sunday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0506',
    name: '어린이날 대체공휴일',
    date: '2024-05-06',
    year: 2024,
    month: 5,
    day: 6,
    day_of_week: 'Monday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0515',
    name: '석가탄신일',
    date: '2024-05-15',
    year: 2024,
    month: 5,
    day: 15,
    day_of_week: 'Wednesday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0606',
    name: '현충일',
    date: '2024-06-06',
    year: 2024,
    month: 6,
    day: 6,
    day_of_week: 'Thursday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0815',
    name: '광복절',
    date: '2024-08-15',
    year: 2024,
    month: 8,
    day: 15,
    day_of_week: 'Thursday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0916',
    name: '추석 연휴',
    date: '2024-09-16',
    year: 2024,
    month: 9,
    day: 16,
    day_of_week: 'Monday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0917',
    name: '추석',
    date: '2024-09-17',
    year: 2024,
    month: 9,
    day: 17,
    day_of_week: 'Tuesday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_0918',
    name: '추석 연휴',
    date: '2024-09-18',
    year: 2024,
    month: 9,
    day: 18,
    day_of_week: 'Wednesday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_1003',
    name: '개천절',
    date: '2024-10-03',
    year: 2024,
    month: 10,
    day: 3,
    day_of_week: 'Thursday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_1009',
    name: '한글날',
    date: '2024-10-09',
    year: 2024,
    month: 10,
    day: 9,
    day_of_week: 'Wednesday',
    type: 'public' as const,
  },
  {
    id: 'hol_2024_1225',
    name: '크리스마스',
    date: '2024-12-25',
    year: 2024,
    month: 12,
    day: 25,
    day_of_week: 'Wednesday',
    type: 'public' as const,
  },
];

export const mockHolidays2024 = mockHolidays2024Raw.map(h => Holiday.fromJSON(h));

/**
 * Mock fetch implementation
 */
export function mockFetch(data: any, ok: boolean = true, status: number = 200) {
  return jest.fn().mockResolvedValue({
    ok,
    status,
    json: jest.fn().mockResolvedValue(data),
  });
}

/**
 * Mock fetch for network errors
 */
export function mockFetchError(error: Error) {
  return jest.fn().mockRejectedValue(error);
}

/**
 * Create success API response envelope
 */
export function createSuccessResponse(data: any[]) {
  return {
    result: true,
    data,
  };
}

/**
 * Create error API response envelope
 */
export function createErrorResponse(message: string) {
  return {
    result: false,
    error: { message },
  };
}
