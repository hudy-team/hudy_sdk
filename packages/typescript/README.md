# @hudy-sdk/sdk

Official TypeScript/JavaScript SDK for the Hudy Korean Public Holiday API.

[![npm version](https://badge.fury.io/js/%40hudy-sdk%2Fsdk.svg)](https://badge.fury.io/js/%40hudy-sdk%2Fsdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Smart Caching** - Intelligent year-based TTL for optimal performance
📅 **Business Day Calculations** - Count business days, skip weekends and holidays
🔒 **Type Safety** - Full TypeScript type definitions included
⚡ **Auto Retry** - Exponential backoff for failed requests
🎯 **Simple API** - Easy-to-use async/await interface

## Installation

```bash
npm install @hudy-sdk/sdk
# or
yarn add @hudy-sdk/sdk
# or
pnpm add @hudy-sdk/sdk
```

## Quick Start

```typescript
import { HudyClient } from '@hudy-sdk/sdk';

const client = new HudyClient({
  apiKey: 'hd_live_your_api_key_here'
});

// Get all holidays for 2024
const holidays = await client.getHolidays(2024);
holidays.forEach(h => {
  console.log(`${h.date} (${h.day_of_week}): ${h.name}`);
  console.log(`  Type: ${h.type}, Public: ${h.is_public}`);
});

// Check if a date is a holiday
const isHoliday = await client.isHoliday(new Date(2024, 0, 1)); // January 1, 2024
console.log(isHoliday); // true

// Get business days between two dates
const businessDays = await client.getBusinessDays(
  new Date(2024, 0, 1),
  new Date(2024, 11, 31)
);
console.log(`Business days in 2024: ${businessDays}`);
```

## API Reference

### Constructor

```typescript
new HudyClient(options: ClientOptions)
```

**Options:**
- `apiKey` (required): Your API key starting with `hd_live_`
- `baseUrl` (optional): API base URL (default: `https://api.hudy.co.kr`)
- `timeout` (optional): Request timeout in milliseconds (default: `10000`)
- `cache` (optional): Cache configuration
  - `enabled` (boolean): Enable/disable caching (default: `true`)
  - `ttl` (number): Custom TTL in seconds (default: auto-calculated based on year)
- `retry` (optional): Retry configuration
  - `enabled` (boolean): Enable/disable retry (default: `true`)
  - `maxRetries` (number): Maximum retry attempts (default: `3`)
  - `initialDelay` (number): Initial delay in ms (default: `1000`)
  - `maxDelay` (number): Maximum delay in ms (default: `10000`)
  - `backoffFactor` (number): Backoff multiplier (default: `2`)

### Methods

#### getHolidays(year: number): Promise<Holiday[]>

Get all holidays for a specific year.

```typescript
const holidays = await client.getHolidays(2024);
```

#### getHolidaysByRange(from: Date, to: Date): Promise<Holiday[]>

Get holidays within a date range (inclusive).

**Note:** The backend API only supports fetching by year, so this method fetches full year(s) and filters the results client-side. For optimal performance with caching, prefer using year-based queries when possible.

```typescript
const holidays = await client.getHolidaysByRange(
  new Date(2024, 0, 1),
  new Date(2024, 2, 31)
);
```

#### isHoliday(date: Date): Promise<boolean>

Check if a specific date is a holiday.

```typescript
const isHoliday = await client.isHoliday(new Date(2024, 0, 1));
```

#### getBusinessDays(from: Date, to: Date): Promise<number>

Count business days between two dates (excluding weekends and holidays).

```typescript
const count = await client.getBusinessDays(
  new Date(2024, 0, 1),
  new Date(2024, 11, 31)
);
```

#### getNextBusinessDay(from: Date): Promise<Date>

Get the next business day after a given date.

```typescript
const nextDay = await client.getNextBusinessDay(new Date(2024, 0, 1));
```

#### addBusinessDays(from: Date, days: number): Promise<Date>

Add N business days to a date.

```typescript
const futureDate = await client.addBusinessDays(new Date(2024, 0, 1), 10);
```

#### isBusinessDay(date: Date): Promise<boolean>

Check if a date is a business day.

```typescript
const isBusiness = await client.isBusinessDay(new Date(2024, 0, 2));
```

#### getCacheStats(): CacheStats

Get cache statistics.

```typescript
const stats = client.getCacheStats();
console.log(`Cache hits: ${stats.hits}, misses: ${stats.misses}`);
```

#### clearCache(): void

Clear all cached data.

```typescript
client.clearCache();
```

## Types

### Holiday

```typescript
class Holiday {
  id: string;
  name: string;
  date: string;           // ISO 8601 (YYYY-MM-DD)
  year: number;
  month: number;
  day: number;
  day_of_week: string;    // e.g., "Monday", "Tuesday"
  type: 'public' | 'custom';

  // Computed convenience properties
  get is_public(): boolean;  // type === 'public'
  get is_custom(): boolean;  // type === 'custom'
}
```

## Error Handling

The SDK throws `HudyError` for API errors:

```typescript
import { HudyError, ErrorCode } from '@hudy-sdk/sdk';

try {
  const holidays = await client.getHolidays(2024);
} catch (error) {
  if (error instanceof HudyError) {
    console.error(`Error: ${error.message}`);
    console.error(`Code: ${error.code}`);
    console.error(`Status: ${error.statusCode}`);
    console.error(`Retryable: ${error.retryable}`);
  }
}
```

**Error Codes:**
- `NETWORK_ERROR` - Network connectivity issue
- `TIMEOUT` - Request timeout
- `UNAUTHORIZED` - Invalid API key (401)
- `FORBIDDEN` - Access forbidden (403)
- `NOT_FOUND` - Resource not found (404)
- `RATE_LIMITED` - Rate limit exceeded (429)
- `BAD_REQUEST` - Invalid request (400)
- `INTERNAL_ERROR` - Server error (5xx)
- `INVALID_RESPONSE` - Malformed API response

## Advanced Usage

### Custom Configuration

```typescript
const client = new HudyClient({
  apiKey: 'hd_live_your_key',
  baseUrl: 'https://custom.api.com',
  timeout: 5000,
  cache: {
    enabled: true,
    ttl: 3600, // 1 hour
  },
  retry: {
    enabled: true,
    maxRetries: 5,
    initialDelay: 500,
    maxDelay: 30000,
    backoffFactor: 2,
  },
});
```

### Disable Caching

```typescript
const client = new HudyClient({
  apiKey: 'hd_live_your_key',
  cache: { enabled: false },
});
```

### Business Day Utilities

For offline calculation without API calls:

```typescript
import { BusinessDayCalculator, formatDate } from '@hudy-sdk/sdk';

// Fetch holidays once
const holidays = await client.getHolidays(2024);

// Create calculator
const calculator = new BusinessDayCalculator(holidays);

// Use calculator for multiple operations (no API calls)
const isBusinessDay = calculator.isBusinessDay(new Date(2024, 0, 2));
const count = calculator.countBusinessDays(
  new Date(2024, 0, 1),
  new Date(2024, 11, 31)
);
const nextDay = calculator.getNextBusinessDay(new Date(2024, 0, 1));
```

## License

MIT

## Links

- [API Documentation](https://www.hudy.co.kr/#docs)
- [GitHub Repository](https://github.com/hudy-team/hudy_sdk)
- [Report Issues](https://github.com/hudy-team/hudy_sdk/issues)
