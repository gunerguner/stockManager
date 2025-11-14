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

// AI修改: 添加版本号导入和打印功能
// 从 package.json 导入版本号
// @ts-ignore - package.json 不需要类型定义
import { version } from '../package.json';

// 在应用启动时打印版本号
console.log(
  `%c Stock Manager v${version} `,
  'background: #1890ff; color: #fff; padding: 4px 8px; border-radius: 4px; font-weight: bold;'
);

const loginPath = '/login';

/**
 * @see  https://umijs.org/zh-CN/plugins/plugin-initial-state
 * @note Umi 4 中 initialStateConfig 已被移除，loading 状态由框架自动处理
 * */
export async function getInitialState(): Promise<{
  settings?: Partial<ProLayoutProps>;
  currentUser?: API.CurrentUser;
  fetchUserInfo?: () => Promise<API.CurrentUser | undefined>;
}> {
  const fetchUserInfo = async () => {
    try {
      const result = await queryCurrentUser();
      if (result.status == 1) {
        return result.info;
      } else if (result.status == 302) {
        history.push(loginPath);
      }
    } catch (error) {
      history.push(loginPath);
    }
    return undefined;
  };
  // 如果是登录页面，不执行
  if (history.location.pathname !== loginPath) {
    const currentUser = await fetchUserInfo();
    return {
      fetchUserInfo,
      currentUser,
      settings: defaultSettings,
    };
  }
  return {
    fetchUserInfo,
    settings: defaultSettings,
  };
}

/**
 * 动态 Logo 组件
 * 根据主题自动切换 logo
 */
const DynamicLogo: React.FC = () => {
  const { actualTheme } = useModel('theme');
  const { initialState } = useModel('@@initialState');
  const settings = initialState?.settings as typeof defaultSettings;

  const logoUrl = actualTheme === 'dark' 
    ? (settings?.logoDark || settings?.logo)
    : (settings?.logoLight || settings?.logo);

  return <img src={logoUrl} alt="logo" style={{ height: '32px' }} />;
};

// https://umijs.org/zh-CN/plugins/plugin-layout
// @ts-ignore - Umi 4 的 rightContentRender 类型定义与实际使用不一致，这里忽略类型检查
export const layout: RuntimeConfig['layout'] = ({ initialState }) => {
  return {
    ...initialState?.settings,
    rightContentRender: () => <RightContent />,
    disableContentMargin: false,
    waterMarkProps: {
      content: initialState?.currentUser?.name,
    },
    footerRender: () => <Footer />,
    onPageChange: () => {
      const { location } = history;
      // 如果没有登录，重定向到 login
      if (!initialState?.currentUser && location.pathname !== loginPath) {
        history.push(loginPath);
      }
    },
    menuHeaderRender: undefined,
    // 使用自定义 logo 渲染（放在最后，覆盖 settings 中的 logo）
    logo: <DynamicLogo />,
  };
};

const codeMessage: Record<number, string> = {
  200: '服务器成功返回请求的数据。',
  201: '新建或修改数据成功。',
  202: '一个请求已经进入后台排队（异步任务）。',
  204: '删除数据成功。',
  400: '发出的请求有错误，服务器没有进行新建或修改数据的操作。',
  401: '用户没有权限（令牌、用户名、密码错误）。',
  403: '用户得到授权，但是访问是被禁止的。',
  404: '发出的请求针对的是不存在的记录，服务器没有进行操作。',
  405: '请求方法不被允许。',
  406: '请求的格式不可得。',
  410: '请求的资源被永久删除，且不会再得到的。',
  422: '当创建一个对象时，发生一个验证错误。',
  500: '服务器发生错误，请检查服务器。',
  502: '网关错误。',
  503: '服务不可用，服务器暂时过载或维护。',
  504: '网关超时。',
};


/** 异常处理程序
 * @see https://beta-pro.ant.design/docs/request-cn
 * @note Umi 4 中错误处理后不应该再抛出错误,否则会导致通知无法显示
 */
const errorHandler = (error: any) => {
  const { response } = error;
  
  if (response && response.status) {
    const errorText = codeMessage[response.status] || response.statusText;
    const { status, url } = response;

    notification.error({
      message: `请求错误 ${status}: ${url}`,
      description: errorText,
    });
  } else if (!response) {
    // 网络错误或请求超时
    notification.error({
      message: '网络异常',
      description: '您的网络发生异常，无法连接服务器',
    });
  }

};

/**
 * 请求拦截器：自动添加 CSRF Token 到请求头
 * 对于非 GET 请求，自动从 Cookie 中读取 CSRF token 并添加到请求头
 */
const requestInterceptor = (url: string, options: any) => {
  const method = options.method?.toUpperCase() || 'GET';
  
  // GET、HEAD、OPTIONS 请求不需要 CSRF token
  if (['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    return { url, options };
  }
  
  // 获取 CSRF token
  const csrfToken = getCsrfToken();
  
  if (csrfToken) {
    const headers = options.headers || {};
    headers['X-CSRFToken'] = csrfToken;
    return {
      url,
      options: {
        ...options,
        headers,
      },
    };
  }
  
  return { url, options };
};

/**
 * 响应拦截器：只拦截错误，显示错误通知
 * @note Umi 4 的响应拦截器接收的是 axios response 对象，需要取 data 字段
 */
const responseInterceptor = (response: any) => {
  // Umi 4 中 response 是 axios response 对象，需要取 data 字段
  const data = response?.data || response;
  
  // 只处理错误情况（status === 0）
  if (data && data.message && data.status === 0) {
    const { message } = data;
    
    // 显示错误通知
    notification.error({
      message: '操作失败',
      description: message,
    });
  }
  
  return response;
};

// https://umijs.org/zh-CN/plugins/plugin-request
export const request: RequestConfig = {
  timeout: 10000,
  errorConfig: {
    errorHandler,
  },
  requestInterceptors: [requestInterceptor],
  responseInterceptors: [responseInterceptor],
};

/**
 * innerProvider 配置
 * 在 Umi Model Provider 之后注入主题配置
 * 这样可以在组件中使用 useModel
 */
export function innerProvider(container: React.ReactNode) {
  return <ThemeConfigProvider>{container}</ThemeConfigProvider>;
}

/**
 * 主题配置提供者组件
 * 使用 Ant Design 的 ConfigProvider 实现主题切换
 * 支持所有组件（包括 Modal.confirm 等静态方法）
 */
function ThemeConfigProvider({ children }: { children: React.ReactNode }) {
  const { actualTheme } = useModel('theme');

  // 动态更新 document 的 data-theme 属性，用于自定义样式
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', actualTheme);
  }, [actualTheme]);

  return (
    <ConfigProvider
      theme={{
        algorithm: actualTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <App>
        {children}
      </App>
    </ConfigProvider>
  );
}
