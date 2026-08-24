/** 股票类型配置：[内部键, 显示名称, API类型(可选)] */
const STOCK_TYPE_CONFIGS: Array<[string, string, string?]> = [
  ['isNew', '新股'],
  ['sh60', '沪市（非新股）', 'SH60'],
  ['sz00', '深市（非新股）', 'SZ00'],
  ['sz300', '创业板（非新股）', 'SZ300'],
  ['sh688', '科创板（非新股）', 'SH688'],
  ['bj', '北交所（非新股）', 'BJ'],
  ['fundAB', '分级基金', 'FUNDAB'],
  ['fundIn', '场内基金', 'FUNDIN'],
  ['conv', '可转债', 'CONV'],
  ['hk', '港股通', 'HK'],
];

/** 按行业无申万分类时的类型展示名（与 StockType 文案一致） */
const STOCK_TYPE_SHORT_LABELS: Record<string, string> = {
  SH60: '沪市',
  SZ00: '深市',
  SZ300: '创业板',
  SH688: '科创板',
  BJ: '北交所',
  FUNDAB: '分级基金',
  FUNDIN: '场内基金',
  CONV: '可转债',
  HK: '港股通',
  OTHER: '其它',
};

const FALLBACK_TYPE_KEYS = STOCK_TYPE_CONFIGS.filter(([, , apiType]) => apiType).map(
  ([key]) => key,
);

/** 固定垫底：分级基金 → 场内基金 → 可转债 → 港股通 → 逆回购 */
const PINNED_TAIL_KEYS = ['fundAB', 'fundIn', 'conv', 'hk', 'incomeCash'] as const;
const PINNED_TAIL_ORDER = new Map<string, number>(
  PINNED_TAIL_KEYS.map((key, index) => [key, index]),
);

const API_TYPE_MAP = new Map(
  STOCK_TYPE_CONFIGS.filter(([, , apiType]) => apiType).map(([key, , apiType]) => [apiType!, key]),
);

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

export type BuildAnalysisOptions = {
  incomeCash?: number;
};

const emptyStat = (key: string, type: string): AnalysisModel => ({
  key,
  type,
  count: 0,
  profit: 0,
  loss: 0,
  netIncome: 0,
  stocks: [],
});

const addStockToStat = (stat: AnalysisModel, stock: API.Stock, offsetTotal: number) => {
  const profit = offsetTotal > 0 ? offsetTotal : 0;
  const loss = offsetTotal < 0 ? offsetTotal : 0;

  stat.profit += profit;
  stat.loss += loss;
  stat.count++;
  stat.netIncome += offsetTotal;
  stat.stocks.push({
    code: stock.code,
    name: stock.name,
    profit,
    loss,
    netIncome: offsetTotal,
    holdCount: stock.holdCount,
  });
};

export const compareAnalysisWithPinnedTail = (
  a: AnalysisModel,
  b: AnalysisModel,
  compare: (left: AnalysisModel, right: AnalysisModel) => number,
): number => {
  const aPin = PINNED_TAIL_ORDER.get(a.key);
  const bPin = PINNED_TAIL_ORDER.get(b.key);
  if (aPin !== undefined && bPin !== undefined) {
    return aPin - bPin;
  }
  if (aPin !== undefined) return 1;
  if (bPin !== undefined) return -1;
  return compare(a, b);
};

export const sortAnalysisList = (
  analysisList: AnalysisModel[],
  field: 'profit' | 'loss' | 'netIncome',
  order: 'ascend' | 'descend',
): AnalysisModel[] =>
  [...analysisList].sort((a, b) =>
    compareAnalysisWithPinnedTail(a, b, (left, right) => {
      const diff = left[field] - right[field];
      return order === 'descend' ? -diff : diff;
    }),
  );

const appendIncomeCash = (analysisList: AnalysisModel[], incomeCash: number) => {
  if (incomeCash > 0) {
    analysisList.push({
      key: 'incomeCash',
      type: '逆回购',
      count: 1,
      profit: incomeCash,
      loss: 0,
      netIncome: incomeCash,
      stocks: [],
    });
  }
};

export const computeOverallProfitLoss = (
  data: API.Stock[],
  incomeCash = 0,
): { totalProfit: number; totalLoss: number } => {
  let totalProfit = 0;
  let totalLoss = 0;

  for (const stock of data) {
    if (stock.offsetTotal > 0) totalProfit += stock.offsetTotal;
    else if (stock.offsetTotal < 0) totalLoss += stock.offsetTotal;
  }

  if (incomeCash > 0) totalProfit += incomeCash;

  return { totalProfit, totalLoss };
};

export const buildAnalysisByStockType = (
  data: API.Stock[],
  options: BuildAnalysisOptions = {},
): AnalysisModel[] => {
  const { incomeCash = 0 } = options;

  const stats = new Map<string, AnalysisModel>(
    STOCK_TYPE_CONFIGS.map(([key, label]) => [key, emptyStat(key, label)]),
  );

  for (const stock of data) {
    const { stockType, isNew, offsetTotal } = stock;
    const key = isNew ? 'isNew' : API_TYPE_MAP.get(stockType);
    const stat = key ? stats.get(key) : undefined;
    if (stat) {
      addStockToStat(stat, stock, offsetTotal);
    }
  }

  const analysisList = [...stats.values()];
  appendIncomeCash(analysisList, incomeCash);
  return analysisList;
};

export const buildAnalysisByIndustry = (
  data: API.Stock[],
  options: BuildAnalysisOptions = {},
): AnalysisModel[] => {
  const { incomeCash = 0 } = options;
  const industryStats = new Map<string, AnalysisModel>();
  const fallbackStats = new Map<string, AnalysisModel>();

  for (const stock of data) {
    const industry = stock.swIndustry;
    if (industry?.code && industry.name) {
      let stat = industryStats.get(industry.code);
      if (!stat) {
        stat = emptyStat(`sw:${industry.code}`, industry.name);
        industryStats.set(industry.code, stat);
      }
      addStockToStat(stat, stock, stock.offsetTotal);
      continue;
    }

    const apiType = stock.stockType;
    const fallbackKey = API_TYPE_MAP.get(apiType) ?? 'other';
    const label = STOCK_TYPE_SHORT_LABELS[apiType] ?? '其它';
    let stat = fallbackStats.get(fallbackKey);
    if (!stat) {
      stat = emptyStat(fallbackKey, label);
      fallbackStats.set(fallbackKey, stat);
    }
    addStockToStat(stat, stock, stock.offsetTotal);
  }

  const industryList = [...industryStats.values()];
  const fallbackList = [...FALLBACK_TYPE_KEYS, 'other']
    .filter((key) => fallbackStats.has(key))
    .map((key) => fallbackStats.get(key)!);

  const analysisList = [...industryList, ...fallbackList];
  appendIncomeCash(analysisList, incomeCash);
  return analysisList;
};
