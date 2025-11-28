import { LogoutOutlined, SettingOutlined } from '@ant-design/icons';
import { Avatar, Dropdown } from 'antd';
import { history, useModel } from '@umijs/max';
import { stringify } from 'querystring';
import { logout } from '@/services/api';
import styles from './index.less';

// ==================== 组件 ====================

const AvatarDropdown: React.FC = () => {
  const { initialState, setInitialState } = useModel('@@initialState');
  const { resetStockData } = useModel('stocks');

  const currentUser = initialState?.currentUser;
  if (!currentUser?.name) return null;

  const handleLogout = async () => {
    try {
      await logout();
      setInitialState?.((state) => ({ ...state, currentUser: undefined }));
      resetStockData();

      setTimeout(() => {
        history.replace({
          pathname: '/login',
          search: stringify({ redirect: history.location.pathname }),
        });
      }, 50);
    } catch (error) {
      console.error('登出失败:', error);
    }
  };

  const menuItems = [
    { key: 'settings', label: '设置', icon: <SettingOutlined />, onClick: () => history.push('/account') },
    { key: 'logout', label: '退出', icon: <LogoutOutlined />, onClick: handleLogout },
  ];

  return (
    <Dropdown menu={{ items: menuItems, className: styles.menu }}>
      <span className={`${styles.action} ${styles.account}`}>
        <Avatar size="small" className={styles.avatar} src={currentUser.avatar} alt={currentUser.name} />
        <span className={`${styles.name} anticon`}>{currentUser.name}</span>
      </span>
    </Dropdown>
  );
};

export default AvatarDropdown;
