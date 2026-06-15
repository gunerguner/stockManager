import { useCallback, useState } from 'react';
import {
  DeleteOutlined,
  LoadingOutlined,
  LogoutOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { App, Avatar, Dropdown, Row } from 'antd';
import { history, useModel } from '@umijs/max';
import { clearCache, logout, updateDividend } from '@/services/api';
import { hasApiData, isApiSuccess } from '@/utils/api';
import styles from './index.less';

// ==================== 组件 ====================

const AvatarDropdown: React.FC = () => {
  const [dividendLoading, setDividendLoading] = useState(false);
  const [cacheLoading, setCacheLoading] = useState(false);
  const { initialState, setInitialState } = useModel('@@initialState');
  const { resetStockData } = useModel('stocks');
  const { modal } = App.useApp();

  const currentUser = initialState?.currentUser;
  const canAdmin = currentUser?.access === 'admin';

  const handleLogout = async () => {
    try {
      await logout();
      setInitialState?.((state) => ({ ...state, currentUser: undefined }));
      resetStockData();

      setTimeout(() => {
        const params = new URLSearchParams({ redirect: history.location.pathname });
        history.replace({
          pathname: '/login',
          search: params.toString(),
        });
      }, 50);
    } catch (error) {
      // 登出失败由全局 errorHandler 处理
    }
  };

  const handleDividendUpdate = useCallback(() => {
    modal.confirm({
      title: '确定更新除权信息？',
      async onOk() {
        try {
          setDividendLoading(true);
          const response = await updateDividend({
            timeout: 120000,
            skipErrorHandler: true,
          });

          if (hasApiData(response)) {
            modal.info({
              title: response.data.length > 0 ? '有更新股票' : '无更新股票',
              content: (
                <>
                  {response.data.map((dividend) => (
                    <Row key={dividend.code}>
                      {dividend.code} - {dividend.name}
                    </Row>
                  ))}
                </>
              ),
            });
          }
        } catch (error) {
          modal.error({
            title: '操作失败',
            content: '更新除权信息失败，请稍后重试',
          });
        } finally {
          setDividendLoading(false);
        }
      },
    });
  }, [modal]);

  const handleOpenAdmin = useCallback(() => {
    window.open('/sys/admin/', '_blank');
  }, []);

  const handleClearCache = useCallback(() => {
    modal.confirm({
      title: '确定清理全部 Redis 缓存？',
      content: '将删除本应用所有缓存数据，下次访问会重新从数据库或接口加载。',
      okType: 'danger',
      async onOk() {
        try {
          setCacheLoading(true);
          const response = await clearCache();

          if (isApiSuccess(response)) {
            modal.success({
              title: '缓存已清理',
              content: `已删除 ${response.data?.deletedCount ?? 0} 个 key`,
            });
          }
        } catch {
          modal.error({
            title: '操作失败',
            content: '清理缓存失败，请稍后重试',
          });
        } finally {
          setCacheLoading(false);
        }
      },
    });
  }, [modal]);

  if (!currentUser?.name) return null;

  const menuItems = [
    { key: 'settings', label: '设置', icon: <SettingOutlined />, onClick: () => history.push('/account') },
    ...(canAdmin
      ? [
          {
            key: 'dividend',
            label: '更新除权信息',
            icon: dividendLoading ? <LoadingOutlined /> : <SyncOutlined />,
            disabled: dividendLoading,
            onClick: handleDividendUpdate,
          },
          {
            key: 'admin',
            label: '管理',
            icon: <SafetyCertificateOutlined />,
            onClick: handleOpenAdmin,
          },
          {
            key: 'clearCache',
            label: '清理缓存',
            icon: cacheLoading ? <LoadingOutlined /> : <DeleteOutlined />,
            disabled: cacheLoading,
            danger: true,
            onClick: handleClearCache,
          },
        ]
      : []),
    { key: 'logout', label: '退出', icon: <LogoutOutlined />, onClick: handleLogout },
  ];

  return (
    <Dropdown menu={{ items: menuItems, className: styles.menu }}>
      <span className={`${styles.action} ${styles.account}`}>
        <Avatar size="small" className={styles.avatar} src={currentUser.avatar} alt={currentUser.name} />
        <span>{currentUser.name}</span>
      </span>
    </Dropdown>
  );
};

export default AvatarDropdown;
