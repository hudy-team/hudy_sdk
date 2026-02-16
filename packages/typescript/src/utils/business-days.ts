/**
 * Business day calculation utilities
 *
 * Functions to calculate business days between dates,
 * skipping weekends and holidays.
 */

import { Holiday } from '../types';
import { formatDate, isWeekend, addDays } from './date';

/**
 * Business day calculator with holiday awareness
 */
export class BusinessDayCalculator {
  private holidaySet: Set<string>; // YYYY-MM-DD format

  constructor(holidays: Holiday[]) {
    this.holidaySet = new Set(holidays.map((h) => h.date));
  }

  /**
   * Check if a date is a business day
   */
  isBusinessDay(date: Date): boolean {
    // Weekend check
    if (isWeekend(date)) {
      return false;
    }

    // Holiday check
    const dateStr = formatDate(date);
    return !this.holidaySet.has(dateStr);
  }

  /**
   * Count business days between two dates (inclusive)
   */
  countBusinessDays(from: Date, to: Date): number {
    if (from > to) {
      throw new Error('from date must be before or equal to to date');
    }

    let count = 0;
    const current = new Date(from);

    while (current <= to) {
      if (this.isBusinessDay(current)) {
        count++;
      }
      current.setDate(current.getDate() + 1);
    }

    return count;
  }

  /**
   * Get the next business day after the given date
   * If the given date is a business day, returns the next one
   */
  getNextBusinessDay(from: Date): Date {
    let current = addDays(from, 1);

    while (!this.isBusinessDay(current)) {
      current = addDays(current, 1);
    }

    return current;
  }

  /**
   * Get the previous business day before the given date
   * If the given date is a business day, returns the previous one
   */
  getPreviousBusinessDay(from: Date): Date {
    let current = addDays(from, -1);

    while (!this.isBusinessDay(current)) {
      current = addDays(current, -1);
    }

    return current;
  }

  /**
   * Add N business days to a date
   * If days is negative, subtracts business days
   */
  addBusinessDays(from: Date, days: number): Date {
    if (days === 0) {
      return new Date(from);
    }

    const direction = days > 0 ? 1 : -1;
    const remaining = Math.abs(days);
    let current = new Date(from);
    let added = 0;

    while (added < remaining) {
      current = addDays(current, direction);
      if (this.isBusinessDay(current)) {
        added++;
      }
    }

    return current;
  }

  /**
   * Get all business days in a range (inclusive)
   */
  getBusinessDaysInRange(from: Date, to: Date): Date[] {
    if (from > to) {
      throw new Error('from date must be before or equal to to date');
    }

    const businessDays: Date[] = [];
    const current = new Date(from);

    while (current <= to) {
      if (this.isBusinessDay(current)) {
        businessDays.push(new Date(current));
      }
      current.setDate(current.getDate() + 1);
    }

    return businessDays;
  }
}
