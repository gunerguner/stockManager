import React, { useState, useCallback } from 'react';
import { Button, Row, Space, App } from 'antd';
import ProCard from '@ant-design/pro-card';
import { history } from '@umijs/max';
import { updateDividend } from '../../services/api';
import { RESPONSE_STATUS } from '@/utils/constants';

const Admin: React.FC = () => {
  const [dividendLoading, setDividendLoading] = useState(false);
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
    window.open('/sys/admin', '_blank');
  }, []);

  return (
    <ProCard gutter={[0, 16]}>
      <Space size="middle">
        <Button type="primary" onClick={handleDividendUpdate} loading={dividendLoading}>
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
