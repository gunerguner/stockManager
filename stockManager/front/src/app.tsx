import React, { useEffect } from 'react';
import type { ProLayoutProps } from '@ant-design/pro-layout';
import { notification, ConfigProvider, theme, App } from 'antd';
import type { RequestConfig, RuntimeConfig } from '@umijs/max';
import { history, useModel } from '@umijs/max';
import RightContent from '@/components/RightContent';
import Footer from '@/components/Footer';
import defaultSettings from '../config/defaultSettings';

import { getCurrentUser as queryCurrentUser } from './services/api';
import { getCsrfToken } from '@/utils';
import { RESPONSE_STATUS, HTTP_CODE_MESSAGE } from '@/utils/constants';
// @ts-ignore
import { version } from '../package.json';

console.log(
  `%c Stock Manager v${version} `,
  'background: #1890ff; color: #fff; padding: 4px 8px; border-radius: 4px; font-weight: bold;'
);

const loginPath = '/login';
export async function getInitialState(): Promise<{
  settings?: Partial<ProLayoutProps>;
  currentUser?: API.CurrentUser;
  fetchUserInfo?: () => Promise<API.CurrentUser | undefined>;
}> {
  const fetchUserInfo = async () => {
    try {
      const result = await queryCurrentUser();
      if (result.status === RESPONSE_STATUS.SUCCESS) return result.info;
      if (result.status === RESPONSE_STATUS.UNAUTHORIZED) history.push(loginPath);
    } catch (error) {
      history.push(loginPath);
    }
    return undefined;
  };

  const isLoginPage = history.location.pathname === loginPath;
  const currentUser = isLoginPage ? undefined : await fetchUserInfo();

  return {
    fetchUserInfo,
    currentUser,
    settings: defaultSettings,
  };
}

const DynamicLogo: React.FC = () => {
  const { actualTheme } = useModel('theme');
  const { initialState } = useModel('@@initialState');
  const settings = initialState?.settings as typeof defaultSettings;

  const logoUrl = actualTheme === 'dark' 
    ? (settings?.logoDark || settings?.logo)
    : (settings?.logoLight || settings?.logo);

  return <img src={logoUrl} alt="logo" style={{ height: '32px' }} />;
};

// @ts-ignore
export const layout: RuntimeConfig['layout'] = ({ initialState }) => ({
  ...initialState?.settings,
  rightContentRender: () => <RightContent />,
  disableContentMargin: false,
  waterMarkProps: { content: initialState?.currentUser?.name },
  footerRender: () => <Footer />,
  onPageChange: () => {
    const { location } = history;
    if (!initialState?.currentUser && location.pathname !== loginPath) {
      history.push(loginPath);
    }
  },
  menuHeaderRender: undefined,
  logo: <DynamicLogo />,
});

const errorHandler = (error: any) => {
  const { response } = error;
  
  if (response?.status) {
    const errorText = HTTP_CODE_MESSAGE[response.status] || response.statusText;
    notification.error({
      message: `请求错误 ${response.status}: ${response.url}`,
      description: errorText,
    });
  } else if (!response) {
    notification.error({
      message: '网络异常',
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
  
  if (data?.message && data.status === RESPONSE_STATUS.ERROR) {
    notification.error({
      message: '操作失败',
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

export function innerProvider(container: React.ReactNode) {
  return <ThemeConfigProvider>{container}</ThemeConfigProvider>;
}

function ThemeConfigProvider({ children }: { children: React.ReactNode }) {
  const { actualTheme } = useModel('theme');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', actualTheme);
  }, [actualTheme]);

  return (
    <ConfigProvider
      theme={{
        algorithm: actualTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: { colorPrimary: '#1890ff' },
      }}
    >
      <App>{children}</App>
    </ConfigProvider>
  );
}
