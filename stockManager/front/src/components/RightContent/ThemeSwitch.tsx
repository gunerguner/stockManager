import { Dropdown } from 'antd';
import { SunOutlined, MoonFilled, SyncOutlined } from '@ant-design/icons';
import { useModel } from '@umijs/max';
import type { ThemeMode } from '@/models/theme';
import styles from './index.less';

// ==================== 配置 ====================

const THEME_CONFIG: Record<ThemeMode, { label: string; icon: React.ReactNode }> = {
  light: { label: '白天模式', icon: <SunOutlined /> },
  dark: { label: '暗夜模式', icon: <MoonFilled /> },
  auto: { label: '跟随系统', icon: <SyncOutlined /> },
};

// ==================== 组件 ====================

const ThemeSwitch: React.FC = () => {
  const { themeMode, setThemeMode } = useModel('theme');

  return (
    <Dropdown
      menu={{
        items: Object.entries(THEME_CONFIG).map(([key, { label, icon }]) => ({ key, label, icon })),
        onClick: ({ key }) => setThemeMode(key as ThemeMode),
        selectedKeys: [themeMode],
      }}
      placement="bottomRight"
      arrow
    >
      <span className={`${styles.action} ${styles.account}`} title="切换主题">
        {THEME_CONFIG[themeMode].icon}
      </span>
    </Dropdown>
  );
};

export default ThemeSwitch;
