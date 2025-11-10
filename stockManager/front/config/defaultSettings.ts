
import type { ProLayoutProps } from '@ant-design/pro-components';

const Settings: ProLayoutProps & {
  pwa?: boolean;
  logo?: string;
  logoLight?: string;
  logoDark?: string;
  colorPrimary?: string;
} = {
  navTheme: 'light',
  // 拂晓蓝
  colorPrimary: '#1890ff',
  layout: 'top',
  contentWidth: 'Fluid',
  fixedHeader: false,
  fixSiderbar: true,
  colorWeak: false,
  title: 'Stock Manager',
  pwa: false,
  // 默认 logo（浅色主题）
  logo: 'https://s21.ax1x.com/2025/10/24/pVXld8U.png',
  // 浅色主题 logo
  logoLight: 'https://s21.ax1x.com/2025/10/24/pVXld8U.png',
  // 暗色主题 logo（你需要替换成实际的暗色 logo 地址）
  logoDark: 'https://z3.ax1x.com/2021/04/10/ca6i9S.png', 
  iconfontUrl: '',
};

export default Settings;
