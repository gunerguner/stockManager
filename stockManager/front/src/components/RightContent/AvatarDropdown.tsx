import React, { useCallback, useMemo } from 'react';
import { LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { Avatar, Spin, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { history, useModel } from '@umijs/max';
import { stringify } from 'querystring';
import styles from './index.less';
import { logout } from '@/services/api';

/**
 * 用户头像下拉菜单组件
 * 显示用户头像、名称，并提供设置和退出登录功能
 */
const AvatarDropdown: React.FC = () => {
  const { initialState, setInitialState } = useModel('@@initialState');

  /**
   * 处理用户登出
   * 清除用户状态并重定向到登录页，保存当前路径用于登录后返回
   */
  const handleLogout = useCallback(async () => {
    try {
      await logout();
      
      // 清除用户状态
      if (setInitialState) {
        setInitialState((state) => ({ ...state, currentUser: undefined }));
      }

      const { pathname } = history.location;
      // 从 URL search 参数中获取 redirect
      const urlParams = new URLSearchParams(window.location.search);
      const redirect = urlParams.get('redirect');
      
      // 如果不在登录页且没有重定向参数，则重定向到登录页
      if (window.location.pathname !== '/login' && !redirect) {
        history.replace({
          pathname: '/login',
          search: stringify({ redirect: pathname }),
        });
      }
    } catch (error) {
      console.error('登出失败:', error);
    }
  }, [setInitialState]);

  /**
   * 导航到账户设置页
   */
  const handleNavigateToAccount = useCallback(() => {
    history.push('/account');
  }, []);

  /**
   * 下拉菜单配置
   */
  const menuItems: MenuProps['items'] = useMemo(
    () => [
      {
        key: 'settings',
        label: '设置',
        icon: <SettingOutlined />,
        onClick: handleNavigateToAccount,
      },
      {
        key: 'logout',
        label: '退出',
        icon: <LogoutOutlined />,
        onClick: handleLogout,
      },
    ],
    [handleNavigateToAccount, handleLogout],
  );

  /**
   * 加载状态组件
   */
  const loadingElement = useMemo(
    () => (
      <span className={`${styles.action} ${styles.account}`}>
        <Spin
          size="small"
          style={{
            marginLeft: 8,
            marginRight: 8,
          }}
        />
      </span>
    ),
    [],
  );

  // 检查初始状态是否加载
  if (!initialState) {
    return loadingElement;
  }

  const { currentUser } = initialState;

  // 检查用户信息是否存在
  if (!currentUser || !currentUser.name) {
    return loadingElement;
  }

  return (
    <Dropdown menu={{ items: menuItems, className: styles.menu }}>
      <span className={`${styles.action} ${styles.account}`}>
        <Avatar 
          size="small" 
          className={styles.avatar} 
          src={currentUser.avatar} 
          alt={currentUser.name} 
        />
        <span className={`${styles.name} anticon`}>{currentUser.name}</span>
      </span>
    </Dropdown>
  );
};

export default AvatarDropdown;
