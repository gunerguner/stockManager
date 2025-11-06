import React, { useMemo } from 'react';
import { Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { BulbOutlined, BulbFilled, DesktopOutlined } from '@ant-design/icons';
import { useModel } from '@umijs/max';
import type { ThemeMode } from '@/models/theme';
import styles from './index.less';

/**
 * 主题切换组件
 * 显示在页面右上角，提供白天模式、暗夜模式、跟随系统三个选项
 */
const ThemeSwitch: React.FC = () => {
  const { themeMode, actualTheme, setThemeMode } = useModel('theme');

  /**
   * 下拉菜单项配置
   */
  const menuItems: MenuProps['items'] = useMemo(
    () => [
      {
        key: 'light',
        label: '白天模式',
        icon: <BulbOutlined />,
      },
      {
        key: 'dark',
        label: '暗夜模式',
        icon: <BulbFilled />,
      },
      {
        key: 'auto',
        label: '跟随系统',
        icon: <DesktopOutlined />,
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
   * 根据当前主题选择图标
   */
  const ThemeIcon = actualTheme === 'dark' ? BulbFilled : BulbOutlined;

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
        <ThemeIcon />
      </span>
    </Dropdown>
  );
};

export default ThemeSwitch;
