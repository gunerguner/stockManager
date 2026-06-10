import { notification } from 'antd';
import { history, type RequestConfig } from '@umijs/max';
import { getCsrfToken } from '@/utils/browser';
import { RESPONSE_STATUS, HTTP_CODE_MESSAGE } from '@/utils/constants';
import { LOGIN_PATH } from './constants';

const redirectToLogin = () => {
  if (history.location.pathname !== LOGIN_PATH) {
    history.push(LOGIN_PATH);
  }
};

const errorHandler = (error: any) => {
  const { response } = error;

  if (response?.status) {
    const errorText = HTTP_CODE_MESSAGE[response.status] || response.statusText;
    notification.error({
      title: `请求错误 ${response.status}: ${response.url}`,
      description: errorText,
    });
  } else if (!response) {
    notification.error({
      title: '网络异常',
      description: '您的网络发生异常，无法连接服务器',
    });
  }
};

const requestInterceptor = (url: string, options: any) => {
  const method = options.method?.toUpperCase() || 'GET';

  if (['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    return { url, options };
  }

  const csrfToken = getCsrfToken();
  if (csrfToken) {
    return {
      url,
      options: {
        ...options,
        headers: {
          ...options.headers,
          'X-CSRFToken': csrfToken,
        },
      },
    };
  }

  return { url, options };
};

const responseInterceptor = (response: any) => {
  const data = response?.data || response;

  if (data?.status === RESPONSE_STATUS.UNAUTHORIZED) {
    redirectToLogin();
    return response;
  }

  if (data?.message && data.status === RESPONSE_STATUS.ERROR) {
    notification.error({
      title: '操作失败',
      description: data.message,
    });
  }

  return response;
};

export const request: RequestConfig = {
  timeout: 10000,
  errorConfig: {
    errorHandler,
  },
  requestInterceptors: [requestInterceptor],
  responseInterceptors: [responseInterceptor],
};
