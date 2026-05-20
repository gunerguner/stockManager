import React, { useState, useCallback } from 'react';
import { Button, Row, Space, App } from 'antd';
import ProCard from '@ant-design/pro-card';
import { history, useModel } from '@umijs/max';
import { updateDividend, clearCache } from '../../services/api';
import { RESPONSE_STATUS } from '@/utils/constants';

const Admin: React.FC = () => {
  const [dividendLoading, setDividendLoading] = useState(false);
  const [cacheLoading, setCacheLoading] = useState(false);
  const { initialState } = useModel('@@initialState');
  const canAdmin = initialState?.currentUser?.access === 'admin';
  const { modal } = App.useApp();

  const handleDividendUpdate = useCallback(() => {
    modal.confirm({
      title: '确定更新除权信息？',
      async onOk() {
        try {
          setDividendLoading(true);
          const response = await updateDividend({ timeout: 20000 });

          if (response.status === RESPONSE_STATUS.SUCCESS && response.data) {
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
          } else if (response.status === RESPONSE_STATUS.UNAUTHORIZED) {
            history.push('/login');
          }
        } catch (error) {
          // 更新除权信息失败由全局 errorHandler 处理
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

          if (response.status === RESPONSE_STATUS.SUCCESS) {
            modal.success({
              title: '缓存已清理',
              content: `已删除 ${response.data?.deletedCount ?? 0} 个 key`,
            });
          } else if (response.status === RESPONSE_STATUS.UNAUTHORIZED) {
            history.push('/login');
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

  return (
    <ProCard gutter={[0, 16]}>
      <Space size="middle">
        <Button type="primary" onClick={handleDividendUpdate} loading={dividendLoading}>
          更新除权信息
        </Button>
        <Button type="primary" onClick={handleOpenAdmin}>
          管理
        </Button>
        {canAdmin && (
          <Button danger onClick={handleClearCache} loading={cacheLoading}>
            清理缓存
          </Button>
        )}
      </Space>
    </ProCard>
  );
};

export default Admin;
