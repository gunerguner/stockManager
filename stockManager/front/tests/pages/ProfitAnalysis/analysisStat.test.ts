import {
  buildAnalysisByIndustry,
  buildAnalysisByStockType,
  computeOverallProfitLoss,
  sortAnalysisList,
} from '@/pages/ProfitAnalysis/components/analysisStat';

const stock = (partial: Partial<API.Stock>): API.Stock =>
  ({
    code: 'x',
    name: 'n',
    priceNow: 1,
    offsetToday: 0,
    offsetTodayRatio: 0,
    holdCount: 1,
    holdCost: 1,
    overallCost: 1,
    totalValue: 1,
    totalValueYesterday: 1,
    offsetCurrent: 0,
    offsetCurrentRatio: 0,
    moneyWeightedReturn: 0,
    totalOffsetToday: 0,
    isNew: false,
    stockType: 'SH60',
    holdingDuration: 1,
    offsetTotal: 0,
    ...partial,
  }) as API.Stock;

test('computeOverallProfitLoss splits profit and loss and adds incomeCash', () => {
  const result = computeOverallProfitLoss(
    [stock({ offsetTotal: 10 }), stock({ offsetTotal: -4 }), stock({ offsetTotal: 0 })],
    3,
  );
  expect(result).toEqual({ totalProfit: 13, totalLoss: -4 });
});

test('buildAnalysisByStockType buckets by type and new stock', () => {
  const list = buildAnalysisByStockType(
    [
      stock({ code: 'sh600519', stockType: 'SH60', offsetTotal: 8, isNew: false }),
      stock({ code: 'sz300001', stockType: 'SZ300', offsetTotal: -2, isNew: true }),
    ],
    5,
  );
  const sh60 = list.find((item) => item.key === 'sh60');
  const isNew = list.find((item) => item.key === 'isNew');
  const income = list.find((item) => item.key === 'incomeCash');
  expect(sh60?.profit).toBe(8);
  expect(isNew?.loss).toBe(-2);
  expect(income?.netIncome).toBe(5);
});

test('buildAnalysisByIndustry prefers swIndustry then stock type', () => {
  const list = buildAnalysisByIndustry([
    stock({
      code: 'a',
      swIndustry: { code: '801780', name: '银行' },
      offsetTotal: 3,
    }),
    stock({ code: 'b', stockType: 'HK', offsetTotal: 1 }),
  ]);
  expect(list.find((item) => item.key === 'sw:801780')?.type).toBe('银行');
  expect(list.find((item) => item.key === 'hk')?.netIncome).toBe(1);
});

test('sortAnalysisList pins fund bond hk and incomeCash at tail', () => {
  const sorted = sortAnalysisList(
    [
      { key: 'hk', type: '港股通', count: 1, profit: 9, loss: 0, netIncome: 9, stocks: [] },
      { key: 'sh60', type: '沪市', count: 1, profit: 1, loss: 0, netIncome: 1, stocks: [] },
      { key: 'incomeCash', type: '逆回购', count: 1, profit: 2, loss: 0, netIncome: 2, stocks: [] },
    ],
    'profit',
    'descend',
  );
  expect(sorted.map((item) => item.key)).toEqual(['sh60', 'hk', 'incomeCash']);
});
