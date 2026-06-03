// ==================== 颜色工具 ====================
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

// ==================== 价格格式化 ====================
export const isHkCode = (code?: string): boolean =>
  !!code && code.toLowerCase().startsWith('hk');

export const formatPrice = (value?: number | string | null): string => {
  if (value === undefined || value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const fixed3 = numValue.toFixed(3);
  return fixed3.endsWith('0') ? numValue.toFixed(2) : fixed3;
};

export const formatMarketPrice = (
  value?: number | string | null,
  code?: string,
): string => {
  const num = formatPrice(value);
  if (num === '-') return num;
  return isHkCode(code) ? `$${num}` : num;
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

/** 从 "12.34%" 等形式解析数值 */
export const parsePercent = (text: string): number =>
  parseFloat(text.replace('%', '')) || 0;
