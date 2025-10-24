// https://umijs.org/config/
import { defineConfig } from '@umijs/max';

import defaultSettings from './defaultSettings';
import proxy from './proxy';
import routes from './routes';

const { REACT_APP_ENV } = process.env;

export default defineConfig({
  hash: true,
  
  /**
   * @name 开启 antd
   * @description antd 插件配置
   */
  antd: {
    // 配置 antd 主题
    theme: {
      token: {
        colorPrimary: defaultSettings.colorPrimary || '#1890ff',
      },
    },
  },
  
  /**
   * @name 开启数据流
   * @description dva 改为 model
   */
  model: {
    // 默认开启
  },
  
  /**
   * @name 初始化数据
   * @description initialState 配置
   */
  initialState: {
    // 默认开启
  },
  
  /**
   * @name request 配置
   * @description request 插件配置
   */
  request: {
    // 默认开启
  },
  
  /**
   * @name layout 插件
   * @description ProLayout 配置
   */
  layout: {
    locale: false,
    siderWidth: 160,
    ...defaultSettings,
  },
  
  /**
   * @name 路由配置
   */
  routes,
  
  /**
   * @name 静态资源路径
   * @description 开发环境使用根路径，生产环境使用 /static/
   */
  publicPath: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  
  /**
   * @name 代理配置
   */
  proxy: proxy[REACT_APP_ENV as keyof typeof proxy || 'dev'],
  
  /**
   * @name Fast Refresh 热更新
   */
  fastRefresh: true,
  
  /**
   * @name 禁用 MFSU 以兼容性
   */
  mfsu: false,
  
  /**
   * @name 构建时压缩
   */
  esbuildMinifyIIFE: true,
  
  /**
   * @name 标题
   */
  title: 'Stock Manager',
  
  /**
   * @name favicon 路径
   * @description 网站 favicon，使用 /static/ 路径与 publicPath 保持一致
   */
  favicons: ['/static/favicon.ico'],
});
