import {
  formatAmount,
  formatDecimalRatio,
  formatMarketPrice,
  formatPercent,
  hkNative,
  isHkCode,
  tradeAmountCny,
} from '@/utils/format/stock';

test('isHkCode matches hk prefix case-insensitively', () => {
  expect(isHkCode('hk00700')).toBe(true);
  expect(isHkCode('HK00700')).toBe(true);
  expect(isHkCode('sh600519')).toBe(false);
  expect(isHkCode(undefined)).toBe(false);
});

test('formatMarketPrice uses 2 or 3 decimals and HKD dollar sign', () => {
  expect(formatMarketPrice(10.5)).toBe('10.50');
  expect(formatMarketPrice(10.123)).toBe('10.123');
  expect(formatMarketPrice(10.12, 'hk00700')).toBe('$10.12');
  expect(formatMarketPrice(-10.5, 'hk00700')).toBe('-$10.50');
  expect(formatMarketPrice(null)).toBe('-');
  expect(formatMarketPrice('bad')).toBe('-');
});

test('formatPercent and ratio helpers', () => {
  expect(formatPercent(12.3)).toBe('12.30%');
  expect(formatPercent(null)).toBe('—');
  expect(formatDecimalRatio(0.1234)).toBe('12.34%');
});

test('tradeAmountCny uses amount for HK and cash for DV', () => {
  const buy = { type: 'BUY', price: 10, count: 100, amount: 860, cash: 0 } as API.Operation;
  expect(tradeAmountCny('sh600519', buy)).toBe(1000);
  expect(tradeAmountCny('hk00700', buy)).toBe(860);
  const dv = { type: 'DV', price: 0, count: 100, cash: 0.5 } as API.Operation;
  expect(tradeAmountCny('sh600519', dv)).toBe(50);
});

test('hkNative offsetTotal is null when cleared', () => {
  expect(hkNative.totalValue({ priceNow: 10, holdCount: 100 })).toBe(1000);
  expect(hkNative.offsetCurrent({ priceNow: 12, holdCost: 10, holdCount: 100 })).toBe(200);
  expect(
    hkNative.offsetTotal({ priceNow: 12, overallCost: 10, holdCount: 0 }),
  ).toBeNull();
  expect(
    hkNative.offsetTotal({ priceNow: 12, overallCost: 10, holdCount: 100 }),
  ).toBe(200);
});

test('formatAmount supports grouped CNY and HKD prefix', () => {
  expect(formatAmount(1234.5, { grouped: true })).toBe('1,234.50');
  expect(formatAmount(12.3, { currency: 'hkd' })).toBe('$12.30');
});
