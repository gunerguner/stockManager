import React, { useState, useCallback } from 'react';
import { Modal, Button, Row, Space } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import ProCard from '@ant-design/pro-card';
import { history } from 'umi';
import { updateDividend } from '../../services/api';

/**
 * 管理员页面
 * 提供更新除权信息和跳转后台管理的功能
 */
const Admin: React.FC = () => {
  const [dividendLoading, setDividendLoading] = useState(false);

  /**
   * 处理更新除权信息
   */
  const handleDividendUpdate = useCallback(() => {
    Modal.confirm({
      title: '确定更新除权信息？',
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        try {
          setDividendLoading(true);
          const response = await updateDividend();

          if (response.status === 1 && response.data) {
            const hasUpdates = response.data.length > 0;
            const modalTitle = hasUpdates ? '有更新股票' : '无更新股票';

            Modal.info({
              title: modalTitle,
              content: (
                <>
                  {response.data.map((dividend: string) => (
                    <Row key={dividend}>{dividend}</Row>
                  ))}
                </>
              ),
            });
          } else if (response.status === 302) {
            history.push('/login');
          }
        } catch (error) {
          console.error('更新除权信息失败:', error);
          Modal.error({
            title: '操作失败',
            content: '更新除权信息失败，请稍后重试',
          });
        } finally {
          setDividendLoading(false);
        }
      },
    });
  }, []);

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
