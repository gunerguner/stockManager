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

export type BuildAnalysisResult = {
  analysisList: AnalysisModel[];
  totalProfit: number;
  totalLoss: number;
};

export const buildAnalysisByStockType = (
  data: API.Stock[],
  options: BuildAnalysisOptions = {},
): BuildAnalysisResult => {
  const { incomeCash = 0 } = options;

  const stats = new Map<string, AnalysisModel>(
    STOCK_TYPE_CONFIGS.map(([key, label]) => [
      key,
      { type: label, count: 0, profit: 0, loss: 0, netIncome: 0, stocks: [] },
    ]),
  );

  let totalProfitCny = 0;
  let totalLossCny = 0;

  for (const stock of data) {
    const { stockType, isNew, offsetTotal, code } = stock;
    const key = isNew ? 'isNew' : API_TYPE_MAP.get(stockType);
    const stat = key ? stats.get(key) : undefined;

    // offsetTotal 已统一为人民币
    if (offsetTotal > 0) totalProfitCny += offsetTotal;
    else if (offsetTotal < 0) totalLossCny += offsetTotal;

    if (stat) {
      const profit = offsetTotal > 0 ? offsetTotal : 0;
      const loss = offsetTotal < 0 ? offsetTotal : 0;

      stat.profit += profit;
      stat.loss += loss;
      stat.count++;
      stat.netIncome += offsetTotal;
      stat.stocks.push({
        code,
        name: stock.name,
        profit,
        loss,
        netIncome: offsetTotal,
        holdCount: stock.holdCount,
      });
    }
  }

  const analysisList = [...stats.values()];

  if (incomeCash > 0) {
    analysisList.push({
      type: '逆回购',
      count: 1,
      profit: incomeCash,
      loss: 0,
      netIncome: incomeCash,
      stocks: [],
    });
    totalProfitCny += incomeCash;
  }

  return {
    analysisList,
    totalProfit: totalProfitCny,
    totalLoss: totalLossCny,
  };
};
