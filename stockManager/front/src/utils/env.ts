/**
 * 环境变量工具函数
 * 使用 Umi 内置的环境变量，更加优雅
 */

/**
 * 环境类型
 */
export type EnvType = 'dev' | 'test' | 'pre' | 'prod';

/**
 * 获取当前环境变量
 * 使用 Umi 内置的 UMI_ENV 变量，无需手动处理引号
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