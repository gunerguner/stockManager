import React from 'react';
import { LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { Avatar, Menu, Spin, Dropdown } from 'antd';
import { history, useModel } from 'umi';
import { stringify } from 'querystring';
import styles from './index.less';
import { outLogin } from '@/services/api';

export type GlobalHeaderRightProps = {};

/**
 * 退出登录，并且将当前的 url 保存
 */
const loginOut = async () => {
  await outLogin();
  const { query = {}, pathname } = history.location;
  const { redirect } = query;
  // Note: There may be security issues, please note
  if (window.location.pathname !== '/login' && !redirect) {
    history.replace({
      pathname: '/login',
      search: stringify({
        redirect: pathname,
      }),
    });
  }
};

const AvatarDropdown: React.FC<GlobalHeaderRightProps> = ({}) => {
  const { initialState, setInitialState } = useModel('@@initialState');

  const loading = (
    <span className={`${styles.action} ${styles.account}`}>
      <Spin
        size="small"
        style={{
          marginLeft: 8,
          marginRight: 8,
        }}
      />
    </span>
  );

  if (!initialState) {
    return loading;
  }

  const { currentUser } = initialState;

  if (!currentUser || !currentUser.name) {
    return loading;
  }

  const menu = (
    <Menu
      className={styles.menu}
      items={[
        {
          key: 'settings',
          label: '设置',
          icon: <SettingOutlined />,
          onClick: () => {
            history.push(`/account`);
          },
        },
        {
          key: 'logout',
          label: '退出',
          icon: <LogoutOutlined />,
          onClick: () => {
            if (initialState) {
              setInitialState({ ...initialState, currentUser: undefined });
              loginOut();
            }
          },
        },
      ]}
    />
  );

  return (
    <Dropdown overlay={menu}>
      <span className={`${styles.action} ${styles.account}`}>
        <Avatar size="small" className={styles.avatar} src={currentUser.avatar} alt="avatar" />
        <span className={`${styles.name} anticon`}>{currentUser.name}</span>
      </span>
    </Dropdown>
  );
};

export default AvatarDropdown;
