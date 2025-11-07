import React, { useMemo } from 'react';
import { Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { SunOutlined, MoonFilled, SyncOutlined } from '@ant-design/icons';
import { useModel } from '@umijs/max';
import type { ThemeMode } from '@/models/theme';
import styles from './index.less';

/**
 * 主题切换组件
 * 显示在页面右上角，提供白天模式、暗夜模式、跟随系统三个选项
 */
const ThemeSwitch: React.FC = () => {
  const { themeMode, setThemeMode } = useModel('theme');

  /**
   * 下拉菜单项配置
   */
  const menuItems: MenuProps['items'] = useMemo(
    () => [
      {
        key: 'light',
        label: '白天模式',
        icon: <SunOutlined />,
      },
      {
        key: 'dark',
        label: '暗夜模式',
        icon: <MoonFilled />,
      },
      {
        key: 'auto',
        label: '跟随系统',
        icon: <SyncOutlined />,
      },
    ],
    [],
  );

  /**
   * 菜单点击处理
   */
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    setThemeMode(key as ThemeMode);
  };

  /**
   * 根据当前选中的模式显示对应图标
   * light -> 太阳图标
   * dark -> 月亮图标
   * auto -> 同步图标
   */
  const getCurrentIcon = () => {
    switch (themeMode) {
      case 'light':
        return <SunOutlined />;
      case 'dark':
        return <MoonFilled />;
      case 'auto':
        return <SyncOutlined />;
      default:
        return <SunOutlined />;
    }
  };

  return (
    <Dropdown
      menu={{
        items: menuItems,
        onClick: handleMenuClick,
        selectedKeys: [themeMode],
      }}
      placement="bottomRight"
      arrow
    >
      <span className={`${styles.action} ${styles.account}`} title="切换主题">
        {getCurrentIcon()}
      </span>
    </Dropdown>
  );
};

export default ThemeSwitch;
