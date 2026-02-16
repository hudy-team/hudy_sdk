/**
 * HudyClient tests
 */

import { HudyClient } from '../src/client';
import { HudyError } from '../src/errors';
import { ErrorCode } from '../src/types';
import {
  mockFetch,
  mockFetchError,
  createSuccessResponse,
  createErrorResponse,
  mockHolidays2024Raw,
  mockHolidays2024,
} from './helpers';

// Mock fetch globally
global.fetch = jest.fn();

describe('HudyClient', () => {
  const apiKey = 'hd_live_test123';
  let client: HudyClient;

  beforeEach(() => {
    jest.clearAllMocks();
    client = new HudyClient({
      apiKey,
      cache: { enabled: false }, // Disable cache for most tests
      retry: { enabled: false },  // Disable retry for most tests
    });
  });

  describe('constructor', () => {
    it('should create client with valid API key', () => {
      expect(client).toBeInstanceOf(HudyClient);
    });

    it('should throw error if apiKey is missing', () => {
      expect(() => new HudyClient({ apiKey: '' })).toThrow('apiKey is required');
    });

    it('should throw error if apiKey does not start with hd_live_', () => {
      expect(() => new HudyClient({ apiKey: 'invalid_key' })).toThrow(
        'apiKey must start with hd_live_'
      );
    });

    it('should use default baseUrl', () => {
      const client = new HudyClient({ apiKey });
      expect((client as any).baseUrl).toBe('https://api.hudy.kr');
    });

    it('should accept custom baseUrl', () => {
      const client = new HudyClient({
        apiKey,
        baseUrl: 'https://custom.api.com',
      });
      expect((client as any).baseUrl).toBe('https://custom.api.com');
    });

    it('should use default timeout', () => {
      const client = new HudyClient({ apiKey });
      expect((client as any).timeout).toBe(10000);
    });

    it('should accept custom timeout', () => {
      const client = new HudyClient({ apiKey, timeout: 5000 });
      expect((client as any).timeout).toBe(5000);
    });
  });

  describe('getHolidays', () => {
    it('should fetch holidays for a year', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      const holidays = await client.getHolidays(2024);

      expect(holidays).toHaveLength(mockHolidays2024Raw.length);
      expect(holidays[0].name).toBe('신정');
      expect(holidays[0].date).toBe('2024-01-01');
      expect(holidays[0].type).toBe('public');
      expect(global.fetch).toHaveBeenCalledWith(
        'https://api.hudy.kr/v1/holidays?year=2024',
        expect.objectContaining({
          headers: expect.objectContaining({
            'x-api-key': apiKey,
          }),
        })
      );
    });

    it('should throw error for invalid year (too low)', async () => {
      await expect(client.getHolidays(1899)).rejects.toThrow(
        'Year must be an integer between 1900 and 2100'
      );
    });

    it('should throw error for invalid year (too high)', async () => {
      await expect(client.getHolidays(2101)).rejects.toThrow(
        'Year must be an integer between 1900 and 2100'
      );
    });

    it('should throw error for non-integer year', async () => {
      await expect(client.getHolidays(2024.5)).rejects.toThrow(
        'Year must be an integer between 1900 and 2100'
      );
    });

    it('should handle API error response', async () => {
      const mockResponse = createErrorResponse('Unauthorized');
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      await expect(client.getHolidays(2024)).rejects.toThrow(HudyError);
      await expect(client.getHolidays(2024)).rejects.toMatchObject({
        code: ErrorCode.UNAUTHORIZED,
      });
    });

    it('should handle network error', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network failed'));

      await expect(client.getHolidays(2024)).rejects.toThrow(HudyError);
      await expect(client.getHolidays(2024)).rejects.toMatchObject({
        code: ErrorCode.NETWORK_ERROR,
      });
    });

    it('should handle timeout', async () => {
      const client = new HudyClient({
        apiKey,
        timeout: 100,
        cache: { enabled: false },
      });

      const abortError = new Error('The operation was aborted');
      abortError.name = 'AbortError';

      (global.fetch as jest.Mock).mockRejectedValue(abortError);

      await expect(client.getHolidays(2024)).rejects.toMatchObject({
        code: ErrorCode.TIMEOUT,
      });
    }, 10000);
  });

  describe('getHolidaysByRange', () => {
    it('should fetch holidays within a date range (single year)', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      const from = new Date('2024-02-01');
      const to = new Date('2024-03-31');
      const holidays = await client.getHolidaysByRange(from, to);

      // Should include Feb 9, 10, 11 (설날) and Mar 1 (삼일절)
      expect(holidays.length).toBe(4);
      expect(holidays[0].date).toBe('2024-02-09');
      expect(holidays[3].date).toBe('2024-03-01');
    });

    it('should fetch holidays across multiple years', async () => {
      const mock2024 = createSuccessResponse(mockHolidays2024Raw);
      const mock2025 = createSuccessResponse([
        {
          id: 'hol_2025_0101',
          name: '신정',
          date: '2025-01-01',
          year: 2025,
          month: 1,
          day: 1,
          day_of_week: 'Wednesday',
          type: 'public',
        },
      ]);

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: jest.fn().mockResolvedValue(mock2024),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: jest.fn().mockResolvedValue(mock2025),
        });

      const from = new Date('2024-12-01');
      const to = new Date('2025-01-31');
      const holidays = await client.getHolidaysByRange(from, to);

      // Should include 2024-12-25 (크리스마스) and 2025-01-01 (신정)
      expect(holidays.length).toBe(2);
      expect(holidays[0].date).toBe('2024-12-25');
      expect(holidays[1].date).toBe('2025-01-01');
    });

    it('should throw error if from > to', async () => {
      const from = new Date('2024-12-31');
      const to = new Date('2024-01-01');

      await expect(client.getHolidaysByRange(from, to)).rejects.toThrow(
        'from date must be before or equal to to date'
      );
    });

    it('should handle single day range', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      const date = new Date('2024-01-01');
      const holidays = await client.getHolidaysByRange(date, date);

      expect(holidays.length).toBe(1);
      expect(holidays[0].date).toBe('2024-01-01');
    });
  });

  describe('isHoliday', () => {
    it('should return true for a holiday', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      const result = await client.isHoliday(new Date('2024-01-01'));
      expect(result).toBe(true);
    });

    it('should return false for a non-holiday', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      const result = await client.isHoliday(new Date('2024-01-02'));
      expect(result).toBe(false);
    });
  });

  describe('cache operations', () => {
    beforeEach(() => {
      client = new HudyClient({
        apiKey,
        cache: { enabled: true },
        retry: { enabled: false },
      });
    });

    it('should cache holidays after first fetch', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      // First call
      await client.getHolidays(2024);
      expect(global.fetch).toHaveBeenCalledTimes(1);

      // Second call (should use cache)
      await client.getHolidays(2024);
      expect(global.fetch).toHaveBeenCalledTimes(1); // Still 1
    });

    it('should return cache stats', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      await client.getHolidays(2024);
      await client.getHolidays(2024); // Cache hit

      const stats = client.getCacheStats();
      expect(stats.hits).toBe(1);
      expect(stats.misses).toBe(1);
      expect(stats.size).toBe(1);
    });

    it('should clear cache', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      await client.getHolidays(2024);
      client.clearCache();

      const stats = client.getCacheStats();
      expect(stats.size).toBe(0);
    });

    it('should prune expired entries', async () => {
      const mockResponse = createSuccessResponse(mockHolidays2024Raw);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      await client.getHolidays(2024);
      const pruned = client.pruneCache();

      // No entries should be expired immediately
      expect(pruned).toBe(0);
    });
  });

  describe('retry logic', () => {
    beforeEach(() => {
      client = new HudyClient({
        apiKey,
        cache: { enabled: false },
        retry: {
          enabled: true,
          maxRetries: 2,
          initialDelay: 10,
          backoffFactor: 2,
        },
      });
    });

    it('should retry on retryable errors', async () => {
      const mockResponse = createErrorResponse('Service Unavailable');

      // Fail twice, succeed on third
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: false,
          status: 503,
          json: jest.fn().mockResolvedValue(mockResponse),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 503,
          json: jest.fn().mockResolvedValue(mockResponse),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: jest.fn().mockResolvedValue(createSuccessResponse(mockHolidays2024Raw)),
        });

      const holidays = await client.getHolidays(2024);
      expect(holidays).toHaveLength(mockHolidays2024Raw.length);
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should not retry on non-retryable errors', async () => {
      const mockResponse = createErrorResponse('Unauthorized');
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      await expect(client.getHolidays(2024)).rejects.toThrow(HudyError);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should throw after max retries', async () => {
      const mockResponse = createErrorResponse('Service Unavailable');
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 503,
        json: jest.fn().mockResolvedValue(mockResponse),
      });

      await expect(client.getHolidays(2024)).rejects.toThrow(HudyError);
      expect(global.fetch).toHaveBeenCalledTimes(3); // 1 initial + 2 retries
    });
  });
});
