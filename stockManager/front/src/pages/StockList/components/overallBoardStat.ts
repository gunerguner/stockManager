import { formatAmount, formatDecimalRatio, formatSharePercent } from '@/utils/format/stock';

export type OverallStatKey = Exclude<keyof API.Overall, 'cashFlowList' | 'totalCost'>;

export type OverallStatConfig = {
  key: OverallStatKey;
  title: string;
  showColor?: boolean;
};

export type ResolvedStat = {
  value: string;
  numeric?: number;
};

const STAT_RESOLVERS: Partial<
  Record<OverallStatKey, (data: API.Overall) => ResolvedStat>
> = {
  totalValue: (d) => {
    const pct = formatSharePercent(d.totalValue, d.totalAsset, 0);
    return {
      value: `${formatAmount(d.totalValue, { grouped: true })} (${pct})`,
      numeric: d.totalValue,
    };
  },
  xirrAnnualized: (d) => ({
    value: formatDecimalRatio(d.xirrAnnualized),
    numeric: d.xirrAnnualized,
  }),
  hkdCnyRate: (d) => ({
    value: formatAmount(d.hkdCnyRate ?? 0, { precision: 4 }),
  }),
};

export const resolveOverallBoardStat = (
  key: OverallStatKey,
  data: API.Overall,
): ResolvedStat => {
  const custom = STAT_RESOLVERS[key];
  if (custom) return custom(data);

  const raw = data[key];
  const numeric = typeof raw === 'number' ? raw : 0;
  return { value: formatAmount(numeric), numeric };
};

export const MAIN_STATISTICS: OverallStatConfig[] = [
  { key: 'offsetToday', title: '当日盈亏', showColor: true },
  { key: 'totalAsset', title: '总资产' },
  { key: 'xirrAnnualized', title: 'XIRR年化', showColor: true },
];

export type OverallBoardActions = {
  incomeCash: () => void;
  originCash: () => void;
};

export type OverallStatAction = keyof OverallBoardActions;

export const STAT_ACTIONS: Partial<Record<OverallStatKey, OverallStatAction>> = {
  incomeCash: 'incomeCash',
  originCash: 'originCash',
};

export const EXPANDED_STATISTICS: OverallStatConfig[] = [
  { key: 'offsetCurrent', title: '浮动盈亏', showColor: true },
  { key: 'offsetTotal', title: '累计盈亏', showColor: true },
  { key: 'totalValue', title: '市值', showColor: true },
  { key: 'totalCash', title: '现金' },
  { key: 'incomeCash', title: '其它现金收入' },
  { key: 'originCash', title: '总入金' },
  { key: 'hkdCnyRate', title: '港币汇率 (HKD/CNY)' },
];
