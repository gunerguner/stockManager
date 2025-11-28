/**
 * 工具函数集合
 */

// ==================== 颜色工具 ====================

/**
 * 根据数值返回对应的颜色
 */
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

/**
 * 格式化价格：最少2位小数，最多3位小数
 */
export const formatPrice = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return String(value);

  const rounded = Math.round(numValue * 1000) / 1000;
  const str = rounded.toString();
  const decimalIndex = str.indexOf('.');

  if (decimalIndex === -1 || str.substring(decimalIndex + 1).length < 2) {
    return rounded.toFixed(2);
  }

  return str;
};

// ==================== 环境变量工具 ====================

export type EnvType = 'dev' | 'test' | 'pre' | 'prod';

/**
 * 获取当前环境变量
 */
export const getEnv = (): EnvType | undefined => {
  // @ts-ignore
  const umiEnv = process.env.UMI_ENV;
  // @ts-ignore
  const nodeEnv = process.env.NODE_ENV;

  if (umiEnv) return umiEnv as EnvType;
  if (nodeEnv === 'development') return 'dev';
  return undefined;
};

// ==================== CSRF Token 工具 ====================

/**
 * 从 Cookie 中获取 CSRF Token
 */
export const getCsrfToken = (): string | null => {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');

  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(`${name}=`)) {
      return decodeURIComponent(trimmed.substring(name.length + 1));
    }
  }

  return null;
};
