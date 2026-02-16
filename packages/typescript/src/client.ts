/**
 * HudyClient implementation
 *
 * Main client class for interacting with the Hudy API.
 * Handles authentication, request/response, and caching.
 */

import {
  Holiday,
  ClientOptions,
  ApiResponse,
  CacheStats,
  RetryOptions,
} from './types';
import { HudyError } from './errors';
import { SmartCache } from './cache';
import { BusinessDayCalculator } from './utils/business-days';

export class HudyClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly retryOptions: Required<RetryOptions>;
  private cache: SmartCache | null;

  constructor(options: ClientOptions) {
    if (!options.apiKey) {
      throw new Error('apiKey is required');
    }
    if (!options.apiKey.startsWith('hd_live_')) {
      throw new Error('apiKey must start with hd_live_');
    }

    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl || 'https://api.hudy.co.kr';
    this.timeout = options.timeout || 10000;

    // Initialize cache
    const cacheEnabled = options.cache?.enabled ?? true;
    this.cache = cacheEnabled ? new SmartCache({ ttl: options.cache?.ttl }) : null;

    this.retryOptions = {
      enabled: options.retry?.enabled ?? true,
      maxRetries: options.retry?.maxRetries ?? 3,
      initialDelay: options.retry?.initialDelay ?? 1000,
      maxDelay: options.retry?.maxDelay ?? 10000,
      backoffFactor: options.retry?.backoffFactor ?? 2,
    };
  }

  /**
   * Get holidays for a specific year
   */
  async getHolidays(year: number): Promise<Holiday[]> {
    if (!Number.isInteger(year) || year < 1900 || year > 2100) {
      throw new Error('Year must be an integer between 1900 and 2100');
    }

    // Check cache first
    if (this.cache) {
      const cached = this.cache.get(year);
      if (cached) {
        return cached;
      }
    }

    // Fetch from API
    const url = `${this.baseUrl}/v2/holidays?year=${year}`;
    const holidays = await this.request<Holiday[]>(url);

    // Store in cache
    if (this.cache) {
      this.cache.set(year, holidays);
    }

    return holidays;
  }

  /**
   * Get holidays within a date range
   */
  async getHolidaysByRange(from: Date, to: Date): Promise<Holiday[]> {
    if (from > to) {
      throw new Error('from date must be before or equal to to date');
    }

    const fromYear = from.getFullYear();
    const toYear = to.getFullYear();
    const fromStr = this.formatDate(from);
    const toStr = this.formatDate(to);

    // If single year, fetch that year and filter
    if (fromYear === toYear) {
      const holidays = await this.getHolidays(fromYear);
      return holidays.filter(h => h.date >= fromStr && h.date <= toStr);
    }

    // Multi-year: fetch all years and filter
    const allHolidays: Holiday[] = [];
    for (let year = fromYear; year <= toYear; year++) {
      const yearHolidays = await this.getHolidays(year);
      allHolidays.push(...yearHolidays);
    }

    return allHolidays.filter(h => h.date >= fromStr && h.date <= toStr);
  }

  /**
   * Check if a specific date is a holiday
   */
  async isHoliday(date: Date): Promise<boolean> {
    const year = date.getFullYear();
    const holidays = await this.getHolidays(year);
    const dateStr = this.formatDate(date);
    return holidays.some((h) => h.date === dateStr);
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): CacheStats {
    return (
      this.cache?.getStats() || { hits: 0, misses: 0, size: 0, entries: [] }
    );
  }

  /**
   * Clear all cached data
   */
  clearCache(): void {
    this.cache?.clear();
  }

  /**
   * Remove expired cache entries
   */
  pruneCache(): number {
    return this.cache?.prune() || 0;
  }

  /**
   * Get business days between two dates (inclusive)
   * Automatically fetches holidays for the date range
   */
  async getBusinessDays(from: Date, to: Date): Promise<number> {
    if (from > to) {
      throw new Error('from date must be before or equal to to date');
    }

    const holidays = await this.getHolidaysByRange(from, to);
    const calculator = new BusinessDayCalculator(holidays);
    return calculator.countBusinessDays(from, to);
  }

  /**
   * Get the next business day after a given date
   */
  async getNextBusinessDay(from: Date): Promise<Date> {
    // Fetch holidays for the year and next year (in case we're at year boundary)
    const year = from.getFullYear();
    let holidays = await this.getHolidays(year);

    // If we might cross year boundary, fetch next year too
    const nextDate = new Date(from);
    nextDate.setDate(nextDate.getDate() + 365); // Look ahead up to a year

    if (nextDate.getFullYear() > year) {
      const nextYearHolidays = await this.getHolidays(year + 1);
      // Create new array instead of mutating cached one
      holidays = [...holidays, ...nextYearHolidays];
    }

    const calculator = new BusinessDayCalculator(holidays);
    return calculator.getNextBusinessDay(from);
  }

  /**
   * Add N business days to a date
   */
  async addBusinessDays(from: Date, days: number): Promise<Date> {
    if (days === 0) {
      return new Date(from);
    }

    // Estimate the date range needed (approximate: 1.4x days to account for weekends)
    const estimatedDays = Math.ceil(Math.abs(days) * 1.4) + 14; // +14 buffer for holidays
    const direction = days > 0 ? 1 : -1;
    const estimatedEnd = new Date(from);
    estimatedEnd.setDate(estimatedEnd.getDate() + estimatedDays * direction);

    // Fetch holidays for the range
    const startDate = direction > 0 ? from : estimatedEnd;
    const endDate = direction > 0 ? estimatedEnd : from;
    const holidays = await this.getHolidaysByRange(startDate, endDate);

    const calculator = new BusinessDayCalculator(holidays);
    return calculator.addBusinessDays(from, days);
  }

  /**
   * Check if a date is a business day
   */
  async isBusinessDay(date: Date): Promise<boolean> {
    const year = date.getFullYear();
    const holidays = await this.getHolidays(year);
    const calculator = new BusinessDayCalculator(holidays);
    return calculator.isBusinessDay(date);
  }

  // Private helper methods

  private async request<T>(url: string): Promise<T> {
    return this.retryOptions.enabled
      ? this.requestWithRetry<T>(url)
      : this.executeRequest<T>(url);
  }

  private async requestWithRetry<T>(url: string): Promise<T> {
    let lastError: HudyError | undefined;
    let delay = this.retryOptions.initialDelay;

    for (let attempt = 0; attempt <= this.retryOptions.maxRetries; attempt++) {
      try {
        return await this.executeRequest<T>(url);
      } catch (error) {
        if (!(error instanceof HudyError) || !error.retryable) {
          throw error;
        }

        lastError = error;

        if (attempt < this.retryOptions.maxRetries) {
          await this.sleep(delay);
          delay = Math.min(
            delay * this.retryOptions.backoffFactor,
            this.retryOptions.maxDelay
          );
        }
      }
    }

    throw lastError!;
  }

  private async executeRequest<T>(url: string): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        headers: {
          'x-api-key': this.apiKey,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Parse response
      const json: ApiResponse<any> = await response.json();

      // Check for API-level errors
      if (!json.result) {
        throw HudyError.fromResponse(response.status, json.error.message);
      }

      // Check HTTP status
      if (!response.ok) {
        throw HudyError.fromResponse(
          response.status,
          `HTTP ${response.status}: ${response.statusText}`
        );
      }

      // Transform raw data to Holiday objects if it's a holiday array
      if (Array.isArray(json.data) && json.data.length > 0 && 'type' in json.data[0]) {
        const holidays = json.data.map((item: any) => Holiday.fromJSON(item));
        return holidays as unknown as T;
      }

      return json.data;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof HudyError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw HudyError.timeout(`Request timeout after ${this.timeout}ms`);
        }
        throw HudyError.networkError(error.message);
      }

      throw HudyError.networkError('Unknown error occurred');
    }
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
