// https://umijs.org/config/
import { defineConfig } from '@umijs/max';
import webpack from 'webpack';

import defaultSettings from './defaultSettings';
import proxy from './proxy';
import routes from './routes';

const { REACT_APP_ENV, ANALYZE } = process.env;
const isProduction = process.env.NODE_ENV === 'production';

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
  publicPath: isProduction ? '/static/' : '/',
  
  /**
   * @name 代理配置
   */
  proxy: proxy[REACT_APP_ENV as keyof typeof proxy || 'dev'],
  
  /**
   * @name Fast Refresh 热更新
   */
  fastRefresh: true,
  
  /**
   * @name 启用 MFSU 加速构建
   * @description 开启后可以显著提升构建速度和优化包大小
   */
  mfsu: {
    strategy: 'normal',
  },
  
  /**
   * @name 构建时压缩
   */
  esbuildMinifyIIFE: true,
  
  /**
   * @name 生产环境优化配置
   */
  ...(isProduction && {
    // CSS 压缩
    cssMinifier: 'esbuild',
    
    // JS 压缩
    jsMinifier: 'esbuild',
    
    // 包分析工具
    ...(ANALYZE && {
      analyze: {
        analyzerMode: 'server',
        analyzerPort: 8888,
        openAnalyzer: true,
      },
    }),
  }),
  
  /**
   * @name Webpack 配置优化
   */
  chainWebpack: (config) => {
    // 排除 dayjs 不需要的语言包
    config.plugin('ignore-dayjs-locales').use(webpack.IgnorePlugin, [
      {
        resourceRegExp: /^\.\/locale$/,
        contextRegExp: /dayjs$/,
      },
    ]);
    
    // 生产环境代码分割优化
    if (isProduction) {
      config.optimization.splitChunks({
        chunks: 'all',
        minSize: 20000,
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        cacheGroups: {
          // React 相关库
          react: {
            name: 'react-vendors',
            test: /[\\/]node_modules[\\/](react|react-dom|react-helmet-async)[\\/]/,
            priority: 30,
            reuseExistingChunk: true,
          },
          // Ant Design 相关库
          antd: {
            name: 'antd-vendors',
            test: /[\\/]node_modules[\\/](antd|@ant-design)[\\/]/,
            priority: 25,
            reuseExistingChunk: true,
          },
          // 其他第三方库
          vendors: {
            name: 'vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
            reuseExistingChunk: true,
          },
          // 公共代码
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      });
      
      // 优化运行时 chunk
      config.optimization.runtimeChunk({
        name: 'runtime',
      });
    }
  },
  
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
