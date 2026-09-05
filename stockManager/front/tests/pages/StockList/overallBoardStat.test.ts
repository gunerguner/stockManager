import { resolveOverallBoardStat } from '@/pages/StockList/components/overallBoardStat';

const overall = {
  offsetCurrent: 10,
  offsetTotal: 20,
  totalValue: 4000,
  offsetToday: 1,
  totalCash: 1000,
  incomeCash: 0,
  originCash: 5000,
  totalAsset: 5000,
  totalCost: 5,
  cashFlowList: [],
  xirrAnnualized: 0.1234,
  hkdCnyRate: 0.86,
} as API.Overall;

test('totalValue includes share percent of totalAsset', () => {
  const stat = resolveOverallBoardStat('totalValue', overall);
  expect(stat.numeric).toBe(4000);
  expect(stat.value).toContain('4,000.00');
  expect(stat.value).toContain('80%');
});

test('xirrAnnualized formats as percent', () => {
  const stat = resolveOverallBoardStat('xirrAnnualized', overall);
  expect(stat.value).toBe('12.34%');
  expect(stat.numeric).toBe(0.1234);
});

test('hkdCnyRate uses 4 decimal places', () => {
  expect(resolveOverallBoardStat('hkdCnyRate', overall).value).toBe('0.8600');
});
