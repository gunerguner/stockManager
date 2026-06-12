import type { ProLayoutProps } from '@ant-design/pro-components';

/** 与 src/theme/themeConfig.ts 中 PRIMARY_COLOR 保持一致 */
const PRIMARY_COLOR = '#1677ff';

const Settings: ProLayoutProps & {
  pwa?: boolean;
  logo?: string;
  logoLight?: string;
  logoDark?: string;
  colorPrimary?: string;
} = {
  navTheme: 'light',
  colorPrimary: PRIMARY_COLOR,
  layout: 'top',
  contentWidth: 'Fluid',
  fixedHeader: true,
  fixSiderbar: true,
  colorWeak: false,
  title: 'Stock Manager',
  pwa: false,
  logo: 'https://s21.ax1x.com/2025/10/24/pVXld8U.png',
  logoLight: 'https://s21.ax1x.com/2025/10/24/pVXld8U.png',
  logoDark: 'https://z3.ax1x.com/2021/04/10/ca6i9S.png',
  iconfontUrl: '',
};

export default Settings;
