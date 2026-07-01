// https://umijs.org/config/
import path from 'path';
import { defineConfig } from '@umijs/max';

import defaultSettings from './defaultSettings';

const variablesPath = path.join(__dirname, '../src/styles/variables.less').replace(/\\/g, '/');
import proxy from './proxy';
import routes from './routes';

const { UMI_ENV } = process.env;
const isProduction = process.env.NODE_ENV === 'production';

export default defineConfig({
  hash: true,

  lessLoader: {
    additionalData: `@import "${variablesPath}";`,
  },

  /**
   * @name 开启 antd
   * @description antd 插件配置
   */
  antd: {
    // Ant Design 6 使用 CSS 变量模式
    style: 'css',
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
  publicPath: isProduction ? '/static/' : '/',

  /**
   * @name 代理配置
   */
  proxy: proxy[UMI_ENV as keyof typeof proxy || 'dev'],

  /**
   * @name Fast Refresh 热更新
   */
  fastRefresh: true,

  /**
   * @name Rust bundler（@utoo/pack）
   * @description 与 MFSU 二选一
   */
  utoopack: {},
  mfsu: false,

  /**
   * @name 标题
   */
  title: 'Stock Manager',
});
