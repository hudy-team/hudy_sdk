# Hudy SDK

Official SDKs for the Hudy Korean Public Holiday API.

## Packages

- **[@hudy/sdk](./packages/typescript)** - TypeScript/JavaScript SDK
- **[hudy-sdk](./packages/python)** - Python SDK

## Features

✨ **Smart Caching** - Intelligent caching with year-based TTL
📅 **Business Day Calculations** - Calculate business days, skip weekends and holidays
🔒 **Type Safety** - Full TypeScript and Python type definitions
⚡ **Auto Retry** - Built-in retry logic with exponential backoff
🎯 **Simple API** - Easy-to-use interface for holiday queries

## Quick Start

### TypeScript/JavaScript

```bash
npm install @hudy/sdk
```

```typescript
import { HudyClient } from '@hudy/sdk';

const client = new HudyClient({ apiKey: 'hd_live_...' });
const holidays = await client.getHolidays(2024);
```

### Python

```bash
pip install hudy-sdk
```

```python
from hudy import HudyClient

client = HudyClient(api_key='hd_live_...')
holidays = client.get_holidays(2024)
```

## Documentation

See individual package READMEs for detailed documentation:
- [TypeScript SDK Documentation](./packages/typescript/README.md)
- [Python SDK Documentation](./packages/python/README.md)

## Development

```bash
# Install dependencies
npm install

# Build all packages
npm run build

# Run tests
npm run test

# Format code
npm run format
```

## License

MIT
