/**
 * 工具函数集合
 * 包含颜色、环境变量、CSRF Token 等通用工具函数
 */

// ==================== 颜色工具 ====================

/**
 * 根据数值返回对应的颜色
 * @param value - 数值
 * @returns 颜色字符串：正数返回 'red'，负数返回 'green'，零返回空字符串
 */
export const colorFromValue = (value: number): string => {
  return value > 0 ? 'red' : value < 0 ? 'green' : '';
};

// ==================== 环境变量工具 ====================

/**
 * 环境类型
 */
export type EnvType = 'dev' | 'test' | 'pre' | 'prod';

/**
 * 获取当前环境变量
 * 使用 Umi 内置的 UMI_ENV 变量
 * @returns 环境类型，生产构建且未设置时返回 undefined
 */
export const getEnv = (): EnvType | undefined => {
  // @ts-ignore - UMI_ENV 是 Umi 自动注入的
  const umiEnv = process.env.UMI_ENV;
  // @ts-ignore - NODE_ENV 是 webpack 自动注入的
  const nodeEnv = process.env.NODE_ENV;

  // 优先使用 UMI_ENV
  if (umiEnv) {
    return umiEnv as EnvType;
  }

  // 开发环境默认为 'dev'
  if (nodeEnv === 'development') {
    return 'dev';
  }

  // 生产构建且未设置 UMI_ENV，返回 undefined（不显示环境标签）
  return undefined;
};

// ==================== CSRF Token 工具 ====================

/**
 * 从 Cookie 中获取 CSRF Token
 * @returns CSRF Token 或 null
 */
export const getCsrfToken = (): string | null => {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');

  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith(`${name}=`)) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }

  return null;
};