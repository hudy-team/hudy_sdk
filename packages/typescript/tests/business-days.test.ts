/**
 * Business day calculation tests
 */

import { BusinessDayCalculator } from '../src/utils/business-days';
import { mockHolidays2024, createMockHoliday } from './helpers';

describe('BusinessDayCalculator', () => {
  let calculator: BusinessDayCalculator;

  beforeEach(() => {
    calculator = new BusinessDayCalculator(mockHolidays2024);
  });

  describe('isBusinessDay', () => {
    it('should return true for weekdays that are not holidays', () => {
      const monday = new Date('2024-01-08'); // Not a holiday
      expect(calculator.isBusinessDay(monday)).toBe(true);
    });

    it('should return false for Saturdays', () => {
      const saturday = new Date('2024-01-06');
      expect(calculator.isBusinessDay(saturday)).toBe(false);
    });

    it('should return false for Sundays', () => {
      const sunday = new Date('2024-01-07');
      expect(calculator.isBusinessDay(sunday)).toBe(false);
    });

    it('should return false for public holidays', () => {
      const newYear = new Date('2024-01-01'); // 신정
      expect(calculator.isBusinessDay(newYear)).toBe(false);
    });

    it('should return false for holidays that fall on weekdays', () => {
      const samil = new Date('2024-03-01'); // 삼일절 (Friday)
      expect(calculator.isBusinessDay(samil)).toBe(false);
    });
  });

  describe('countBusinessDays', () => {
    it('should count business days in a week without holidays', () => {
      const from = new Date('2024-01-08'); // Monday
      const to = new Date('2024-01-12'); // Friday
      const count = calculator.countBusinessDays(from, to);
      expect(count).toBe(5);
    });

    it('should exclude weekends', () => {
      const from = new Date('2024-01-08'); // Monday
      const to = new Date('2024-01-14'); // Sunday (next week)
      const count = calculator.countBusinessDays(from, to);
      expect(count).toBe(5); // Mon-Fri only
    });

    it('should exclude holidays', () => {
      const from = new Date('2024-02-09'); // Friday (설날 연휴)
      const to = new Date('2024-02-14'); // Wednesday
      // 2024-02-09 (Fri, holiday), 2024-02-10 (Sat, holiday), 2024-02-11 (Sun, holiday)
      // 2024-02-12 (Mon), 2024-02-13 (Tue), 2024-02-14 (Wed)
      const count = calculator.countBusinessDays(from, to);
      expect(count).toBe(3); // Only Mon, Tue, Wed are business days
    });

    it('should handle single day range (business day)', () => {
      const date = new Date('2024-01-08'); // Monday
      const count = calculator.countBusinessDays(date, date);
      expect(count).toBe(1);
    });

    it('should handle single day range (weekend)', () => {
      const date = new Date('2024-01-06'); // Saturday
      const count = calculator.countBusinessDays(date, date);
      expect(count).toBe(0);
    });

    it('should handle single day range (holiday)', () => {
      const date = new Date('2024-01-01'); // 신정
      const count = calculator.countBusinessDays(date, date);
      expect(count).toBe(0);
    });

    it('should count across months', () => {
      const from = new Date('2024-01-29'); // Monday
      const to = new Date('2024-02-02'); // Friday
      // Jan 29 (Mon), 30 (Tue), 31 (Wed), Feb 1 (Thu), 2 (Fri)
      const count = calculator.countBusinessDays(from, to);
      expect(count).toBe(5);
    });

    it('should handle long ranges', () => {
      const from = new Date('2024-01-01');
      const to = new Date('2024-12-31');
      const count = calculator.countBusinessDays(from, to);

      // 2024 is a leap year (366 days)
      // Approximate: 52 weeks = 104 weekend days, 17 public holidays
      // ~245 business days (varies based on holiday positions)
      expect(count).toBeGreaterThan(240);
      expect(count).toBeLessThan(250);
    });
  });

  describe('getNextBusinessDay', () => {
    it('should return next day if current is Friday and next is Monday', () => {
      const friday = new Date('2024-01-05');
      const next = calculator.getNextBusinessDay(friday);
      expect(next.toISOString().split('T')[0]).toBe('2024-01-08');
    });

    it('should skip weekends', () => {
      const saturday = new Date('2024-01-06');
      const next = calculator.getNextBusinessDay(saturday);
      expect(next.toISOString().split('T')[0]).toBe('2024-01-08'); // Monday
    });

    it('should skip holidays', () => {
      const beforeNewYear = new Date('2023-12-29'); // Friday
      // Need to create calculator with 2024-01-01 holiday
      const holidays = [createMockHoliday('2024-01-01', '신정')];
      const calc = new BusinessDayCalculator(holidays);
      const next = calc.getNextBusinessDay(beforeNewYear);
      expect(next.toISOString().split('T')[0]).toBe('2024-01-02'); // Tuesday
    });

    it('should skip consecutive holidays', () => {
      const beforeChuseok = new Date('2024-09-13'); // Friday
      // 2024-09-16 (Mon, holiday), 2024-09-17 (Tue, holiday), 2024-09-18 (Wed, holiday)
      const next = calculator.getNextBusinessDay(beforeChuseok);
      expect(next.toISOString().split('T')[0]).toBe('2024-09-19'); // Thursday
    });

    it('should handle business day input', () => {
      const monday = new Date('2024-01-08');
      const next = calculator.getNextBusinessDay(monday);
      expect(next.toISOString().split('T')[0]).toBe('2024-01-09'); // Tuesday
    });
  });

  describe('addBusinessDays', () => {
    it('should add positive business days', () => {
      const from = new Date('2024-01-08'); // Monday
      const result = calculator.addBusinessDays(from, 5);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-15'); // Next Monday
    });

    it('should add zero business days', () => {
      const from = new Date('2024-01-08');
      const result = calculator.addBusinessDays(from, 0);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-08');
    });

    it('should subtract negative business days', () => {
      const from = new Date('2024-01-15'); // Monday
      const result = calculator.addBusinessDays(from, -5);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-08'); // Previous Monday
    });

    it('should skip weekends when adding', () => {
      const friday = new Date('2024-01-05');
      const result = calculator.addBusinessDays(friday, 1);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-08'); // Monday
    });

    it('should skip holidays when adding', () => {
      const beforeNewYear = new Date('2023-12-29'); // Friday
      const holidays = [
        createMockHoliday('2024-01-01', '신정'),
        createMockHoliday('2024-01-02', '대체공휴일'),
      ];
      const calc = new BusinessDayCalculator(holidays);
      const result = calc.addBusinessDays(beforeNewYear, 1);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-03'); // Wednesday
    });

    it('should handle adding days across multiple weeks', () => {
      const from = new Date('2024-01-08'); // Monday
      const result = calculator.addBusinessDays(from, 10);
      // 10 business days = 2 full weeks
      expect(result.toISOString().split('T')[0]).toBe('2024-01-22'); // Monday
    });

    it('should handle subtracting days across multiple weeks', () => {
      const from = new Date('2024-01-22'); // Monday
      const result = calculator.addBusinessDays(from, -10);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-08'); // Monday
    });

    it('should handle adding days that land on weekend (start from weekend)', () => {
      const saturday = new Date('2024-01-06');
      const result = calculator.addBusinessDays(saturday, 1);
      expect(result.toISOString().split('T')[0]).toBe('2024-01-08'); // Tuesday (skip Sat, Sun, Mon)
    });

    it('should handle complex range with holidays', () => {
      const from = new Date('2024-02-08'); // Thursday before 설날
      // 2024-02-09 (Fri, holiday), 2024-02-10 (Sat, holiday), 2024-02-11 (Sun, holiday)
      // Next business day is 2024-02-12 (Mon)
      const result = calculator.addBusinessDays(from, 1);
      expect(result.toISOString().split('T')[0]).toBe('2024-02-12'); // Monday
    });
  });

  describe('edge cases', () => {
    it('should handle empty holiday list', () => {
      const calc = new BusinessDayCalculator([]);
      const from = new Date('2024-01-08'); // Monday
      const to = new Date('2024-01-12'); // Friday
      const count = calc.countBusinessDays(from, to);
      expect(count).toBe(5);
    });

    it('should handle calculator with no holidays initialized', () => {
      const calc = new BusinessDayCalculator([]);
      const monday = new Date('2024-01-01'); // Monday (would be holiday normally)
      expect(calc.isBusinessDay(monday)).toBe(true); // No holidays, so it's a business day
    });

    it('should handle dates at year boundaries', () => {
      const holidays = [
        createMockHoliday('2023-12-25', 'Christmas'),
        createMockHoliday('2024-01-01', '신정'),
      ];
      const calc = new BusinessDayCalculator(holidays);

      const from = new Date('2023-12-22'); // Friday
      const to = new Date('2024-01-05'); // Friday
      const count = calc.countBusinessDays(from, to);

      // Should count business days across the year boundary
      expect(count).toBeGreaterThan(5);
    });

    it('should handle same day twice', () => {
      const monday = new Date('2024-01-08');
      const count = calculator.countBusinessDays(monday, monday);
      expect(count).toBe(1);
    });
  });
});
