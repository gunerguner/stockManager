// ==================== 颜色工具（A 股：红涨绿跌） ====================

/** @deprecated 组件内请使用 useProfitLossColors */
export const PROFIT_COLOR = '#ff4d4f';
/** @deprecated 组件内请使用 useProfitLossColors */
export const LOSS_COLOR = '#389e0d';

export const colorFromValue = (
  value: number,
  colors?: { profitColor?: string; lossColor?: string },
): string | undefined => {
  const profit = colors?.profitColor ?? PROFIT_COLOR;
  const loss = colors?.lossColor ?? LOSS_COLOR;
  return value > 0 ? profit : value < 0 ? loss : undefined;
};

// ==================== 市场 / 货币 ====================
export type MarketCurrency = 'cny' | 'hkd';

export const isHkCode = (code?: string): boolean =>
  !!code && code.toLowerCase().startsWith('hk');

export const toMarketCurrency = (isHk: boolean): MarketCurrency => (isHk ? 'hkd' : 'cny');

export const marketCurrency = (code?: string): MarketCurrency => toMarketCurrency(isHkCode(code));

export const toXueqiuStockUrl = (code: string): string =>
  `https://xueqiu.com/S/${isHkCode(code) ? `HK${code.slice(2)}` : code}`;

export const toCnyByCurrency = (
  currency: MarketCurrency,
  amount: number,
  hkdCnyRate: number,
): number => (currency === 'hkd' ? amount * hkdCnyRate : amount);

export const toCnyAmount = (code: string, amount: number, hkdCnyRate: number): number =>
  toCnyByCurrency(marketCurrency(code), amount, hkdCnyRate);

// ==================== 数字格式化 ====================
const formatNumber = (value: number, precision: number = 2, grouped = false): string =>
  grouped
    ? value.toLocaleString('en-US', {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      })
    : value.toFixed(precision);

/** 给已格式化的数字串加港币 $ 前缀（保留负号位置） */
const withHkdSymbol = (numStr: string): string =>
  numStr.startsWith('-') ? `-$${numStr.slice(1)}` : `$${numStr}`;

// ==================== 价格格式化（可变精度 2~3 位，无千分位） ====================
export const formatMarketPrice = (value: number | string | null, code?: string): string => {
  if (value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const fixed3 = Math.abs(numValue).toFixed(3);
  const abs = fixed3.endsWith('0') ? Math.abs(numValue).toFixed(2) : fixed3;
  const num = numValue < 0 ? `-${abs}` : abs;

  return isHkCode(code) ? withHkdSymbol(num) : num;
};

// ==================== 金额格式化（固定精度，可千分位） ====================
export type FormatAmountOptions = {
  code?: string;
  currency?: MarketCurrency;
  grouped?: boolean;
};

export const formatAmount = (
  value: number,
  options?: FormatAmountOptions,
  precision: number = 2,
): string => {
  const { grouped = false, code, currency = marketCurrency(code) } = options ?? {};

  if (currency === 'hkd') {
    return withHkdSymbol(formatNumber(value, precision));
  }
  return formatNumber(value, precision, grouped);
};

// ==================== 百分比 ====================
/** 数值（已是百分数）→ "x.xx%"，null/NaN → "—" */
export const formatPercent = (value: number | null, precision: number = 2): string =>
  value != null && !Number.isNaN(value) ? `${value.toFixed(precision)}%` : '—';
