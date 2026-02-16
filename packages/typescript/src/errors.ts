/**
 * Custom error classes
 *
 * API-specific errors with proper error codes and messages.
 */

import { ErrorCode } from './types';

export class HudyError extends Error {
  constructor(
    message: string,
    public code: ErrorCode,
    public statusCode?: number,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'HudyError';
    Object.setPrototypeOf(this, HudyError.prototype);
  }

  static fromResponse(status: number, message: string): HudyError {
    switch (status) {
      case 401:
        return new HudyError(message, ErrorCode.UNAUTHORIZED, status, false);
      case 403:
        return new HudyError(message, ErrorCode.FORBIDDEN, status, false);
      case 404:
        return new HudyError(message, ErrorCode.NOT_FOUND, status, false);
      case 429:
        return new HudyError(message, ErrorCode.RATE_LIMITED, status, true);
      case 400:
        return new HudyError(message, ErrorCode.BAD_REQUEST, status, false);
      default:
        return new HudyError(
          message,
          ErrorCode.INTERNAL_ERROR,
          status,
          status >= 500
        );
    }
  }

  static networkError(message: string): HudyError {
    return new HudyError(message, ErrorCode.NETWORK_ERROR, undefined, true);
  }

  static timeout(message: string): HudyError {
    return new HudyError(message, ErrorCode.TIMEOUT, undefined, true);
  }

  static invalidResponse(message: string): HudyError {
    return new HudyError(message, ErrorCode.INVALID_RESPONSE, undefined, false);
  }
}
