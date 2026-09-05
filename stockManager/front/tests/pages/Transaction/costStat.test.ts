import { buildCostListByPeriod, parseYearMonth } from '@/pages/Transaction/components/costStat';

test('parseYearMonth splits ISO date', () => {
  expect(parseYearMonth('2024-03-15')).toEqual({ year: '2024', month: '03' });
});

test('buildCostListByPeriod aggregates buy sell dv and cash flow', () => {
  const stocks = [
    { code: 'sh600519', stockType: 'SH60' },
    { code: 'sh113050', stockType: 'CONV' },
  ] as API.Stock[];
  const operations: Record<string, API.Operation[]> = {
    sh600519: [
      { date: '2024-01-10', type: 'BUY', price: 10, count: 100, fee: 5, cash: 0 } as API.Operation,
      { date: '2024-01-20', type: 'SELL', price: 12, count: 50, fee: 3, cash: 0 } as API.Operation,
      { date: '2024-02-01', type: 'DV', price: 0, count: 100, fee: 0, cash: 0.5 } as API.Operation,
    ],
    sh113050: [
      { date: '2024-01-15', type: 'BUY', price: 100, count: 10, fee: 1, cash: 0 } as API.Operation,
    ],
  };
  const years = buildCostListByPeriod(stocks, operations, [
    { date: '2024-01-01', amount: 10000 },
    { date: '2024-02-01', amount: -2000 },
  ]);
  expect(years).toHaveLength(1);
  const y2024 = years[0];
  expect(y2024.normalTradeCount).toBe(2);
  expect(y2024.convTradeCount).toBe(1);
  expect(y2024.dividendCount).toBe(1);
  expect(y2024.buyAmount).toBe(1000 + 1000);
  expect(y2024.sellAmount).toBe(600);
  expect(y2024.fee).toBe(9);
  expect(y2024.cashFlow).toBe(8000);
  expect(y2024.subList?.map((m) => m.id).sort()).toEqual(['01', '02']);
});
