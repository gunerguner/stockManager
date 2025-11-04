/**
 * CSRF Token 工具函数
 * 用于从 Cookie 中获取 CSRF Token 并添加到请求头
 */

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

