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

// ==================== CSRF Token 工具 ====================
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
