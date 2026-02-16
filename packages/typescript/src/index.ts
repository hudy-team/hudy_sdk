/**
 * Main entry point for @hudy/sdk
 *
 * This file exports the public API of the Hudy SDK.
 */

export { HudyClient } from './client';
export { HudyError } from './errors';
export { Holiday } from './types';
export type {
  ClientOptions,
  CacheOptions,
  RetryOptions,
  CacheStats,
  ApiResponse,
  ApiSuccessResponse,
  ApiErrorResponse,
} from './types';
export { ErrorCode } from './types';

// Export utility functions and classes
export { BusinessDayCalculator } from './utils/business-days';
export {
  formatDate,
  parseDate,
  isWeekend,
  addDays,
  isSameDay,
  daysBetween,
} from './utils/date';
