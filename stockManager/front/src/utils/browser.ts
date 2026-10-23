// ==================== 环境变量工具 ====================

export type EnvType = 'dev' | 'test' | 'pre' | 'prod';

export const getEnv = (): EnvType | undefined => {
  // @ts-ignore
  const umiEnv = process.env.UMI_ENV;
  // @ts-ignore
  const nodeEnv = process.env.NODE_ENV;

  if (umiEnv) return umiEnv as EnvType;
  if (nodeEnv === 'development') return 'dev';
  return undefined;
};

/**
 * 环境标签颜色配置
 */
export const ENV_TAG_COLORS = {
  dev: 'orange',
  test: 'green',
  pre: '#87d068',
} as const;

// ==================== CSRF Token 工具 ====================

export const getCsrfToken = (): string | null => {
  const name = 'csrftoken';
  const raw = document.cookie
    .split(';')
    .map((cookie) => cookie.trim())
    .find((cookie) => cookie.startsWith(`${name}=`));
  return raw ? decodeURIComponent(raw.slice(name.length + 1)) : null;
};
