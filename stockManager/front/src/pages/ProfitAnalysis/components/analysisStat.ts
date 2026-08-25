type TypeConfig = {
  key: string;
  label: string;
  apiType?: string;
  shortLabel?: string;
};

const STOCK_TYPES: TypeConfig[] = [
  { key: 'isNew', label: '新股' },
  { key: 'sh60', label: '沪市（非新股）', apiType: 'SH60', shortLabel: '沪市' },
  { key: 'sz00', label: '深市（非新股）', apiType: 'SZ00', shortLabel: '深市' },
  { key: 'sz300', label: '创业板（非新股）', apiType: 'SZ300', shortLabel: '创业板' },
  { key: 'sh688', label: '科创板（非新股）', apiType: 'SH688', shortLabel: '科创板' },
  { key: 'bj', label: '北交所（非新股）', apiType: 'BJ', shortLabel: '北交所' },
  { key: 'fundAB', label: '分级基金', apiType: 'FUNDAB' },
  { key: 'fundIn', label: '场内基金', apiType: 'FUNDIN' },
  { key: 'conv', label: '可转债', apiType: 'CONV' },
  { key: 'hk', label: '港股通', apiType: 'HK' },
];

const TYPE_BY_API = new Map(
  STOCK_TYPES.flatMap((t) => (t.apiType ? [[t.apiType, t] as const] : [])),
);

/** 固定垫底：分级基金 → 场内基金 → 可转债 → 港股通 → 逆回购 */
const PINNED_TAIL = ['fundAB', 'fundIn', 'conv', 'hk', 'incomeCash'];

export type SortField = 'profit' | 'loss' | 'netIncome';

export interface StockDetail {
  code: string;
  name: string;
  profit: number;
  loss: number;
  netIncome: number;
  holdCount?: number;
}

export interface AnalysisModel {
  key: string;
  type: string;
  count: number;
  profit: number;
  loss: number;
  netIncome: number;
  stocks: StockDetail[];
}

const emptyStat = (key: string, type: string): AnalysisModel => ({
  key,
  type,
  count: 0,
  profit: 0,
  loss: 0,
  netIncome: 0,
  stocks: [],
});

const ensureStat = (stats: Map<string, AnalysisModel>, key: string, type: string) => {
  let stat = stats.get(key);
  if (stat) return stat;
  stats.set(key, (stat = emptyStat(key, type)));
  return stat;
};

const addStockToStat = (
  stat: AnalysisModel,
  { offsetTotal: net, code, name, holdCount }: API.Stock,
) => {
  const profit = Math.max(net, 0);
  const loss = Math.min(net, 0);
  stat.profit += profit;
  stat.loss += loss;
  stat.count++;
  stat.netIncome += net;
  stat.stocks.push({ code, name, profit, loss, netIncome: net, holdCount });
};

const withIncomeCash = (list: AnalysisModel[], incomeCash: number) => {
  if (incomeCash > 0) {
    list.push({
      ...emptyStat('incomeCash', '逆回购'),
      count: 1,
      profit: incomeCash,
      netIncome: incomeCash,
    });
  }
  return list;
};

const resolveIndustryBucket = ({ swIndustry, stockType }: API.Stock) => {
  if (swIndustry?.code && swIndustry.name) {
    return { key: `sw:${swIndustry.code}`, type: swIndustry.name };
  }
  const { key = 'other', shortLabel, label = '其它' } = TYPE_BY_API.get(stockType) ?? {};
  return { key, type: shortLabel ?? label };
};

export const sortAnalysisList = (
  list: AnalysisModel[],
  field: SortField,
  order: 'ascend' | 'descend',
) => {
  const dir = order === 'descend' ? -1 : 1;
  return list.toSorted((a, b) => {
    const aPin = PINNED_TAIL.indexOf(a.key);
    const bPin = PINNED_TAIL.indexOf(b.key);
    if (aPin >= 0 && bPin >= 0) return aPin - bPin;
    if (aPin >= 0) return 1;
    if (bPin >= 0) return -1;
    return (a[field] - b[field]) * dir;
  });
};

export const computeOverallProfitLoss = (data: API.Stock[], incomeCash = 0) => {
  let totalProfit = 0;
  let totalLoss = 0;
  for (const { offsetTotal } of data) {
    if (offsetTotal > 0) totalProfit += offsetTotal;
    else if (offsetTotal < 0) totalLoss += offsetTotal;
  }
  if (incomeCash > 0) totalProfit += incomeCash;
  return { totalProfit, totalLoss };
};

export const buildAnalysisByStockType = (data: API.Stock[], incomeCash = 0) => {
  const stats = new Map(STOCK_TYPES.map((t) => [t.key, emptyStat(t.key, t.label)]));
  for (const stock of data) {
    const key = stock.isNew ? 'isNew' : TYPE_BY_API.get(stock.stockType)?.key;
    if (key) addStockToStat(stats.get(key)!, stock);
  }
  return withIncomeCash([...stats.values()], incomeCash);
};

export const buildAnalysisByIndustry = (data: API.Stock[], incomeCash = 0) => {
  const stats = new Map<string, AnalysisModel>();
  for (const stock of data) {
    const { key, type } = resolveIndustryBucket(stock);
    addStockToStat(ensureStat(stats, key, type), stock);
  }
  return withIncomeCash([...stats.values()], incomeCash);
};
