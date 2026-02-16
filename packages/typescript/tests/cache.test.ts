/**
 * SmartCache tests
 */

import { SmartCache } from '../src/cache';
import { mockHolidays2024 } from './helpers';

describe('SmartCache', () => {
  let cache: SmartCache;

  beforeEach(() => {
    cache = new SmartCache();
  });

  describe('basic operations', () => {
    it('should store and retrieve holidays', () => {
      cache.set(2024, mockHolidays2024);
      const retrieved = cache.get(2024);

      expect(retrieved).toEqual(mockHolidays2024);
    });

    it('should return null for cache miss', () => {
      const retrieved = cache.get(2024);
      expect(retrieved).toBeNull();
    });

    it('should overwrite existing entries', () => {
      const firstData = [mockHolidays2024[0]];
      const secondData = mockHolidays2024;

      cache.set(2024, firstData);
      cache.set(2024, secondData);

      const retrieved = cache.get(2024);
      expect(retrieved).toEqual(secondData);
    });

    it('should handle multiple years', () => {
      const holidays2023 = [mockHolidays2024[0]];
      const holidays2024 = mockHolidays2024;

      cache.set(2023, holidays2023);
      cache.set(2024, holidays2024);

      expect(cache.get(2023)).toEqual(holidays2023);
      expect(cache.get(2024)).toEqual(holidays2024);
    });
  });

  describe('expiration', () => {
    it('should set future expiration for future years', () => {
      const futureYear = new Date().getFullYear() + 1;
      cache.set(futureYear, mockHolidays2024);

      const stats = cache.getStats();
      const entry = stats.entries.find(e => e.key === `year:${futureYear}`);

      expect(entry).toBeDefined();
      expect(entry!.expiresAt).toBeGreaterThan(Date.now());
    });

    it('should set long expiration for past years', () => {
      const pastYear = 2020;
      cache.set(pastYear, mockHolidays2024);

      const stats = cache.getStats();
      const entry = stats.entries.find(e => e.key === `year:${pastYear}`);

      expect(entry).toBeDefined();
      // Past years should have very long expiration (365 days)
      const oneYearFromNow = Date.now() + 365 * 24 * 60 * 60 * 1000;
      expect(entry!.expiresAt).toBeGreaterThan(oneYearFromNow - 1000);
    });

    it('should return null for expired entries', () => {
      // Manually create an expired entry
      cache.set(2024, mockHolidays2024);

      // Access private cache to set expiration to the past
      const privateCache = (cache as any).store;
      const entry = privateCache.get('year:2024');
      if (entry) {
        entry.expiresAt = Date.now() - 1000; // Expired 1 second ago
      }

      const retrieved = cache.get(2024);
      expect(retrieved).toBeNull();
    });

    it('should auto-remove expired entries on get', () => {
      cache.set(2024, mockHolidays2024);

      // Expire the entry
      const privateCache = (cache as any).store;
      const entry = privateCache.get('year:2024');
      if (entry) {
        entry.expiresAt = Date.now() - 1000;
      }

      cache.get(2024); // Should remove expired entry

      const stats = cache.getStats();
      expect(stats.size).toBe(0);
    });
  });

  describe('statistics', () => {
    it('should track cache hits', () => {
      cache.set(2024, mockHolidays2024);
      cache.get(2024); // Hit
      cache.get(2024); // Hit

      const stats = cache.getStats();
      expect(stats.hits).toBe(2);
    });

    it('should track cache misses', () => {
      cache.get(2024); // Miss
      cache.get(2025); // Miss

      const stats = cache.getStats();
      expect(stats.misses).toBe(2);
    });

    it('should track cache size', () => {
      cache.set(2023, mockHolidays2024);
      cache.set(2024, mockHolidays2024);
      cache.set(2025, mockHolidays2024);

      const stats = cache.getStats();
      expect(stats.size).toBe(3);
    });

    it('should list cache entries with expiration', () => {
      cache.set(2024, mockHolidays2024);
      cache.set(2025, mockHolidays2024);

      const stats = cache.getStats();
      expect(stats.entries).toHaveLength(2);
      expect(stats.entries[0]).toHaveProperty('key');
      expect(stats.entries[0]).toHaveProperty('expiresAt');
    });

    it('should reset hits and misses separately', () => {
      cache.set(2024, mockHolidays2024);
      cache.get(2024); // Hit
      cache.get(2025); // Miss

      let stats = cache.getStats();
      expect(stats.hits).toBe(1);
      expect(stats.misses).toBe(1);

      // Clear and check stats reset
      cache.clear();
      stats = cache.getStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
    });
  });

  describe('clear and prune', () => {
    it('should clear all entries', () => {
      cache.set(2023, mockHolidays2024);
      cache.set(2024, mockHolidays2024);
      cache.set(2025, mockHolidays2024);

      cache.clear();

      const stats = cache.getStats();
      expect(stats.size).toBe(0);
      expect(cache.get(2024)).toBeNull();
    });

    it('should clear statistics on clear', () => {
      cache.set(2024, mockHolidays2024);
      cache.get(2024); // Hit
      cache.get(2025); // Miss

      cache.clear();

      const stats = cache.getStats();
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
    });

    it('should prune expired entries', () => {
      cache.set(2024, mockHolidays2024);
      cache.set(2025, mockHolidays2024);

      // Expire one entry
      const privateCache = (cache as any).store;
      const entry = privateCache.get('year:2024');
      if (entry) {
        entry.expiresAt = Date.now() - 1000;
      }

      const pruned = cache.prune();
      expect(pruned).toBe(1);

      const stats = cache.getStats();
      expect(stats.size).toBe(1);
      expect(cache.get(2024)).toBeNull();
      expect(cache.get(2025)).not.toBeNull();
    });

    it('should return 0 when no entries to prune', () => {
      cache.set(2024, mockHolidays2024);
      const pruned = cache.prune();
      expect(pruned).toBe(0);
    });
  });

  describe('edge cases', () => {
    it('should handle empty holiday arrays', () => {
      cache.set(2024, []);
      const retrieved = cache.get(2024);
      expect(retrieved).toEqual([]);
    });

    it('should handle year 1900', () => {
      cache.set(1900, mockHolidays2024);
      const retrieved = cache.get(1900);
      expect(retrieved).toEqual(mockHolidays2024);
    });

    it('should handle year 2100', () => {
      cache.set(2100, mockHolidays2024);
      const retrieved = cache.get(2100);
      expect(retrieved).toEqual(mockHolidays2024);
    });

    it('should not mutate stored data', () => {
      const originalData = [...mockHolidays2024];
      cache.set(2024, mockHolidays2024);

      const retrieved = cache.get(2024);
      expect(retrieved).toEqual(originalData);

      // Ensure original is unchanged
      expect(mockHolidays2024).toEqual(originalData);
    });
  });
});
