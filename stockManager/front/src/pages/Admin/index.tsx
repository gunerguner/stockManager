import React, { useState, useCallback } from 'react';
import { Button, Row, Space, App } from 'antd';
import ProCard from '@ant-design/pro-card';
import { history } from '@umijs/max';
import { updateDividend } from '../../services/api';
import { RESPONSE_STATUS } from '@/utils/constants';

/**
 * 管理员页面
 * 提供更新除权信息和跳转后台管理的功能
 */
const Admin: React.FC = () => {
  const [dividendLoading, setDividendLoading] = useState(false);
  const { modal } = App.useApp();

  /**
   * 处理更新除权信息
   */
  const handleDividendUpdate = useCallback(() => {
    modal.confirm({
      title: '确定更新除权信息？',
      icon: null,
      async onOk() {
        try {
          setDividendLoading(true);
          const response = await updateDividend({
            timeout: 20000,
          });

          if (response.status === RESPONSE_STATUS.SUCCESS && response.data) {
            const hasUpdates = response.data.length > 0;
            const modalTitle = hasUpdates ? '有更新股票' : '无更新股票';

            modal.info({
              title: modalTitle,
              icon: null,
              content: (
                <>
                  {response.data.map((dividend: string) => (
                    <Row key={dividend}>{dividend}</Row>
                  ))}
                </>
              ),
            });
          } else if (response.status === RESPONSE_STATUS.UNAUTHORIZED) {
            history.push('/login');
          }
        } catch (error) {
          console.error('更新除权信息失败:', error);
          modal.error({
            title: '操作失败',
            icon: null,
            content: '更新除权信息失败，请稍后重试',
          });
        } finally {
          setDividendLoading(false);
        }
      },
    });
  }, [modal]);

  /**
   * 打开后台管理页面
   */
  const handleOpenAdmin = useCallback(() => {
    window.open('/sys/admin', '_blank');
  }, []);

  return (
    <ProCard gutter={[0, 16]}>
      <Space size="middle">
        <Button
          type="primary"
          onClick={handleDividendUpdate}
          loading={dividendLoading}
        >
          更新除权信息
        </Button>
        <Button type="primary" onClick={handleOpenAdmin}>
          管理
        </Button>
      </Space>
    </ProCard>
  );
};

export default Admin;
