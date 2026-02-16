/**
 * TypeScript type definitions
 *
 * Type definitions for holidays, API responses, and client configuration.
 */

// Holiday type matching the API response
export class Holiday {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly date: string,           // ISO 8601 (YYYY-MM-DD)
    public readonly year: number,
    public readonly month: number,
    public readonly day: number,
    public readonly day_of_week: string,    // e.g., "Monday", "Tuesday"
    public readonly type: 'public' | 'custom'
  ) {}

  get is_public(): boolean {
    return this.type === 'public';
  }

  get is_custom(): boolean {
    return this.type === 'custom';
  }

  static fromJSON(json: any): Holiday {
    return new Holiday(
      json.id,
      json.name,
      json.date,
      json.year,
      json.month,
      json.day,
      json.day_of_week,
      json.type
    );
  }
}

// API envelope types
export interface ApiSuccessResponse<T> {
  result: true;
  data: T;
  // Note: backend does not return meta field
}

export interface ApiErrorResponse {
  result: false;
  error: {
    message: string;
  };
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

// Client configuration
export interface ClientOptions {
  apiKey: string;
  baseUrl?: string;           // default: 'https://api.hudy.kr'
  timeout?: number;            // default: 10000 (10s)
  cache?: CacheOptions;
  retry?: RetryOptions;
}

export interface CacheOptions {
  enabled?: boolean;           // default: true
  ttl?: number;                // seconds, default: auto (year-based)
}

export interface RetryOptions {
  enabled?: boolean;           // default: true
  maxRetries?: number;         // default: 3
  initialDelay?: number;       // ms, default: 1000
  maxDelay?: number;           // ms, default: 10000
  backoffFactor?: number;      // default: 2
}

// Cache statistics
export interface CacheStats {
  hits: number;
  misses: number;
  size: number;
  entries: Array<{
    key: string;
    expiresAt: number;
  }>;
}

// Error types
export enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  RATE_LIMITED = 'RATE_LIMITED',
  BAD_REQUEST = 'BAD_REQUEST',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  INVALID_RESPONSE = 'INVALID_RESPONSE',
}
