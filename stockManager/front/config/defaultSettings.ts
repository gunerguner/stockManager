
import type { ProLayoutProps } from '@ant-design/pro-components';

const Settings: ProLayoutProps & {
  pwa?: boolean;
  logo?: string;
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
  logo: 'https://z3.ax1x.com/2021/04/10/ca6i9S.png',
  iconfontUrl: '',
};

export default Settings;
