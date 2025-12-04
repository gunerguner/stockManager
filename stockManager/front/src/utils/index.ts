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
 * 格式化价格：如果第三位小数非 0 则保留 3 位，否则保留 2 位
 */
export const formatPrice = (value?: number | string | null): string => {
  if (value === undefined || value === null || value === '') return '-';

  const numValue = typeof value === 'string' ? Number(value) : value;
  if (Number.isNaN(numValue)) return '-';

  const fixed3 = numValue.toFixed(3);
  return fixed3.endsWith('0') ? numValue.toFixed(2) : fixed3;
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
