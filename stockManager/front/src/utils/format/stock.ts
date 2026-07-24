// ==================== 市场 / 货币 ====================
export type MarketCurrency = 'cny' | 'hkd';

export const isHkCode = (code?: string): boolean =>
  !!code && code.toLowerCase().startsWith('hk');

export const toXueqiuStockUrl = (code: string): string =>
  `https://xueqiu.com/S/${isHkCode(code) ? `HK${code.slice(2)}` : code}`;

// ==================== 数字格式化 ====================
const formatNumber = (value: number, precision: number = 2, grouped = false): string =>
  grouped
    ? value.toLocaleString('en-US', {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      })
    : value.toFixed(precision);

/** 第三位小数为 0 时保留 2 位，否则保留 3 位（绝对值） */
const formatFlexibleDecimals = (value: number): string => {
  const abs = Math.abs(value);
  const fixed3 = abs.toFixed(3);
  return fixed3.endsWith('0') ? abs.toFixed(2) : fixed3;
};

/** 给已格式化的数字串加港币 $ 前缀（保留负号位置） */
const withHkdSymbol = (numStr: string): string =>
  numStr.startsWith('-') ? `-$${numStr.slice(1)}` : `$${numStr}`;

/** 价格：可变精度 2~3 位，无千分位；港股加 $ */
export const formatMarketPrice = (value: number | string | null, code?: string): string => {
  if (value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const abs = formatFlexibleDecimals(numValue);
  const num = numValue < 0 ? `-${abs}` : abs;
  return isHkCode(code) ? withHkdSymbol(num) : num;
};

export type FormatAmountOptions = {
  currency?: MarketCurrency;
  grouped?: boolean;
  precision?: number;
};

/** 金额：固定精度，可千分位；默认人民币，currency 为 hkd 时加 $ */
export const formatAmount = (value: number, options?: FormatAmountOptions): string => {
  const { grouped = false, currency = 'cny', precision = 2 } = options ?? {};
  const num = formatNumber(value, precision, grouped);
  return currency === 'hkd' ? withHkdSymbol(num) : num;
};

// ==================== 百分比 ====================
/** 数值（已是百分数）→ "x.xx%"，null/NaN → "—" */
export const formatPercent = (value: number | null, precision: number = 2): string =>
  value != null && !Number.isNaN(value) ? `${value.toFixed(precision)}%` : '—';

/** 小数比率（0~1）→ "x.xx%" */
export const formatDecimalRatio = (ratio: number | null, precision: number = 2): string =>
  formatPercent(ratio != null ? ratio * 100 : null, precision);

/** 占比 part/total → "x.xx%" */
export const formatSharePercent = (
  part: number,
  total: number,
  precision: number = 2,
): string => formatPercent(total ? (part / total) * 100 : 0, precision);

// ==================== 交易 / 港币推导 ====================
/** 人民币成交金额：港股用 amount，其它用 price×count */
export const tradeAmountCny = (code: string, op: API.Operation): number =>
  isHkCode(code) ? op.amount ?? 0 : op.price * op.count;

/** 交易说明：除权除息用股息/送转文案，其余用备注 */
export const operationComment = (op: API.Operation): string => {
  if (op.type !== 'DV') return op.comment;

  const parts: string[] = [];
  if (op.cash > 0) parts.push(`每10股股息${formatFlexibleDecimals(op.cash * 10)}`);
  if (op.reserve > 0) parts.push(`每10股转增${formatFlexibleDecimals(op.reserve * 10)}`);
  if (op.stock > 0) parts.push(`每10股送股${formatFlexibleDecimals(op.stock * 10)}`);
  return parts.join(', ');
};

/** 港币口径（由列表已有字段推导，供 tooltip） */
export const hkNative = {
  totalValue: (s: Pick<API.Stock, 'priceNow' | 'holdCount'>) => s.priceNow * s.holdCount,
  offsetCurrent: (s: Pick<API.Stock, 'priceNow' | 'holdCost' | 'holdCount'>) =>
    (s.priceNow - s.holdCost) * s.holdCount,
  offsetToday: (s: Pick<API.Stock, 'offsetToday' | 'holdCount'>) =>
    s.offsetToday * s.holdCount,
  /** 已清仓时摊薄成本被清零，无法还原，返回 null */
  offsetTotal: (s: Pick<API.Stock, 'priceNow' | 'overallCost' | 'holdCount'>): number | null =>
    Math.abs(s.holdCount) < 0.1 ? null : (s.priceNow - s.overallCost) * s.holdCount,
};
