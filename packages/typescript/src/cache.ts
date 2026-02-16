/**
 * Smart caching implementation
 *
 * Implements year-based TTL strategy:
 * - Past years (< current): 1 year TTL (very stable)
 * - Current year: 1 day TTL (may change)
 * - Future years (> current): 1 week TTL (not finalized)
 */

import { Holiday } from './types';

interface CacheEntry<T> {
  data: T;
  expiresAt: number; // timestamp in ms
}

export interface CacheStats {
  hits: number;
  misses: number;
  size: number;
  entries: Array<{
    key: string;
    expiresAt: number;
  }>;
}

export class SmartCache {
  private store: Map<string, CacheEntry<Holiday[]>>;
  private hits: number = 0;
  private misses: number = 0;
  private customTTL?: number; // User-provided override in seconds

  constructor(options?: { ttl?: number }) {
    this.store = new Map();
    this.customTTL = options?.ttl;
  }

  /**
   * Get cached holidays for a year
   */
  get(year: number): Holiday[] | null {
    const key = this.getYearKey(year);
    const entry = this.store.get(key);

    if (!entry) {
      this.misses++;
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      this.misses++;
      return null;
    }

    this.hits++;
    return entry.data;
  }

  /**
   * Store holidays for a year with appropriate TTL
   */
  set(year: number, holidays: Holiday[]): void {
    const key = this.getYearKey(year);
    const ttl = this.getTTL(year);
    const expiresAt = Date.now() + ttl * 1000;

    this.store.set(key, {
      data: holidays,
      expiresAt,
    });
  }

  /**
   * Get cached holidays for a date range.
   * Returns null if any required year is not fully cached.
   * Note: Client now fetches by year and filters, so this may not be used directly.
   */
  getRange(from: Date, to: Date): Holiday[] | null {
    const fromYear = from.getFullYear();
    const toYear = to.getFullYear();

    const fromStr = this.formatDate(from);
    const toStr = this.formatDate(to);

    // If single year, just check that year's cache
    if (fromYear === toYear) {
      const cached = this.get(fromYear);
      if (!cached) return null;

      return cached.filter((h) => h.date >= fromStr && h.date <= toStr);
    }

    // Multi-year range: need all years cached
    const allHolidays: Holiday[] = [];
    for (let year = fromYear; year <= toYear; year++) {
      const cached = this.get(year);
      if (!cached) {
        // Don't increment misses again - get() already did it
        return null;
      }
      allHolidays.push(...cached);
    }

    // Don't increment hits again - the get() calls already did it
    return allHolidays.filter((h) => h.date >= fromStr && h.date <= toStr);
  }

  /**
   * Clear all cached data
   */
  clear(): void {
    this.store.clear();
    this.hits = 0;
    this.misses = 0;
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    return {
      hits: this.hits,
      misses: this.misses,
      size: this.store.size,
      entries: Array.from(this.store.entries()).map(([key, entry]) => ({
        key,
        expiresAt: entry.expiresAt,
      })),
    };
  }

  /**
   * Remove expired entries (garbage collection)
   */
  prune(): number {
    const now = Date.now();
    let removed = 0;

    for (const [key, entry] of this.store.entries()) {
      if (now > entry.expiresAt) {
        this.store.delete(key);
        removed++;
      }
    }

    return removed;
  }

  // Private helpers

  private getYearKey(year: number): string {
    return `year:${year}`;
  }

  /**
   * Get TTL in seconds based on year
   */
  private getTTL(year: number): number {
    // If user provided custom TTL, use it
    if (this.customTTL !== undefined) {
      return this.customTTL;
    }

    // Otherwise use year-based logic
    const currentYear = new Date().getFullYear();

    if (year < currentYear) {
      // Past: 1 year (very stable)
      return 365 * 24 * 60 * 60;
    } else if (year === currentYear) {
      // Current: 1 day (may change)
      return 24 * 60 * 60;
    } else {
      // Future: 1 week (not finalized)
      return 7 * 24 * 60 * 60;
    }
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
}
