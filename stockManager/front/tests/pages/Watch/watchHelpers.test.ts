import {
  calcHistHighDropPct,
  calcRoeFromPbPe,
  formatDecimal,
  formatMarketPriceOrDash,
  isBuyPointTriggered,
  isBuyPointWarning,
  isTrendPointTriggered,
  isTrendPointWarning,
} from '@/pages/Watch/components/watchHelpers';

test('buy point trigger and 5% warning band', () => {
  expect(isBuyPointTriggered(9.9, 10)).toBe(true);
  expect(isBuyPointTriggered(10, 10)).toBe(true);
  expect(isBuyPointTriggered(10.1, 10)).toBe(false);
  expect(isBuyPointWarning(10.4, 10)).toBe(true);
  expect(isBuyPointWarning(10.6, 10)).toBe(false);
  expect(isBuyPointTriggered(10, null)).toBe(false);
});

test('trend point trigger and 5% warning band', () => {
  expect(isTrendPointTriggered(10, 10)).toBe(true);
  expect(isTrendPointTriggered(9.9, 10)).toBe(false);
  expect(isTrendPointWarning(9.6, 10)).toBe(true);
  expect(isTrendPointWarning(9.4, 10)).toBe(false);
});

test('ROE and hist-high drop', () => {
  expect(calcRoeFromPbPe(2, 10)).toBe(20);
  expect(calcRoeFromPbPe(2, 0)).toBeNull();
  expect(calcRoeFromPbPe(null, 10)).toBeNull();
  expect(calcHistHighDropPct(100, 80)).toBe(-20);
  expect(calcHistHighDropPct(0, 80)).toBeNull();
});

test('empty values render as dash', () => {
  expect(formatDecimal(null)).toBe('—');
  expect(formatDecimal(1.234, 2)).toBe('1.23');
  expect(formatMarketPriceOrDash(null)).toBe('—');
  expect(formatMarketPriceOrDash(10.5, 'hk00700')).toBe('$10.50');
});
