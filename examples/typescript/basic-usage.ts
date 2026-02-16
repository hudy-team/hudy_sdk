import { HudyClient } from '@hudy/sdk';

async function main() {
  // Initialize client
  const client = new HudyClient({
    apiKey: process.env.HUDY_API_KEY || 'hd_live_demo',
  });

  try {
    // Example 1: Get all holidays for 2024
    console.log('=== Example 1: Get Holidays for 2024 ===');
    const holidays = await client.getHolidays(2024);
    console.log(`Found ${holidays.length} holidays in 2024:`);
    holidays.forEach((h) => console.log(`  ${h.date}: ${h.name}`));

    // Example 2: Check if today is a holiday
    console.log('\n=== Example 2: Check Today ===');
    const today = new Date();
    const isTodayHoliday = await client.isHoliday(today);
    console.log(`Is today a holiday? ${isTodayHoliday ? 'Yes' : 'No'}`);

    // Example 3: Get holidays in a date range
    console.log('\n=== Example 3: Holidays in Q1 2024 ===');
    const q1Holidays = await client.getHolidaysByRange(
      new Date(2024, 0, 1),
      new Date(2024, 2, 31)
    );
    console.log(`Q1 2024 holidays: ${q1Holidays.length}`);

    // Example 4: Count business days
    console.log('\n=== Example 4: Business Days in 2024 ===');
    const businessDays = await client.getBusinessDays(
      new Date(2024, 0, 1),
      new Date(2024, 11, 31)
    );
    console.log(`Total business days in 2024: ${businessDays}`);

    // Example 5: Get next business day
    console.log('\n=== Example 5: Next Business Day ===');
    const nextBusinessDay = await client.getNextBusinessDay(new Date(2024, 0, 1));
    console.log(`Next business day after 2024-01-01: ${nextBusinessDay.toISOString().split('T')[0]}`);

    // Example 6: Add business days
    console.log('\n=== Example 6: Add Business Days ===');
    const futureDate = await client.addBusinessDays(new Date(2024, 0, 1), 10);
    console.log(`10 business days after 2024-01-01: ${futureDate.toISOString().split('T')[0]}`);

    // Example 7: Cache statistics
    console.log('\n=== Example 7: Cache Statistics ===');
    const stats = client.getCacheStats();
    console.log(`Cache hits: ${stats.hits}, misses: ${stats.misses}, size: ${stats.size}`);

  } catch (error) {
    console.error('Error:', error);
  }
}

main();
