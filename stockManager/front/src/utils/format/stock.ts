// ==================== 颜色工具 ====================
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

// ==================== 价格格式化 ====================
export const isHkCode = (code?: string): boolean =>
  !!code && code.toLowerCase().startsWith('hk');

export const toXueqiuStockUrl = (code: string): string =>
  `https://xueqiu.com/S/${isHkCode(code) ? `HK${code.slice(2)}` : code}`;

const formatNumberAbs = (
  value: number,
  precision: number = 2,
  grouped = false,
): string => {
  const abs = Math.abs(value);
  return grouped
    ? abs.toLocaleString('en-US', {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      })
    : abs.toFixed(precision);
};

export const formatPrice = (value?: number | string | null): string => {
  if (value === undefined || value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const fixed3 = Math.abs(numValue).toFixed(3);
  const absFormatted = fixed3.endsWith('0') ? Math.abs(numValue).toFixed(2) : fixed3;
  return numValue < 0 ? `-${absFormatted}` : absFormatted;
};

export const formatHkdAmount = (
  value: number,
  precision: number = 2,
  grouped = false,
): string => {
  const num = formatNumberAbs(value, precision, grouped);
  return value < 0 ? `-$${num}` : `$${num}`;
};

export const formatMarketPrice = (
  value?: number | string | null,
  code?: string,
): string => {
  const num = formatPrice(value);
  if (num === '-') return num;
  if (!isHkCode(code)) return num;
  return num.startsWith('-') ? `-$${num.slice(1)}` : `$${num}`;
};

// ==================== 金额格式化 ====================
export const formatAmount = (
  value: number,
  precision: number = 2,
  grouped = false,
): string =>
  grouped
    ? value.toLocaleString('en-US', {
        minimumFractionDigits: precision,
        maximumFractionDigits: precision,
      })
    : value.toFixed(precision);

export const formatMarketAmount = (
  value: number,
  code?: string,
  precision: number = 2,
  grouped = false,
): string =>
  isHkCode(code) ? formatHkdAmount(value, precision, grouped) : formatAmount(value, precision, grouped);

export const toCnyAmount = (code: string, amount: number, hkdCnyRate: number): number =>
  isHkCode(code) ? amount * hkdCnyRate : amount;

/** 从 "12.34%" 等形式解析数值 */
export const parsePercent = (text: string): number =>
  parseFloat(text.replace('%', '')) || 0;
