import React, { useState } from 'react';

import { Modal, Button, Row } from 'antd';

import { ExclamationCircleOutlined } from '@ant-design/icons';

import ProCard from '@ant-design/pro-card';
import { history } from 'umi';
import { updateDivident } from '../../services/api';

export default (): React.ReactNode => {
  const [dividentLoading, setDividentLoading] = useState(false);

  const dividentClick = () => {
    Modal.confirm({
      title: '确定更新除权信息？',
      icon: <ExclamationCircleOutlined />,
      async onOk() {
        setDividentLoading(true);
        const response = await updateDivident();
        if (response.status == 1 && !!response.data) {
          const modalTitle = response.data.length > 0 ? '有' : '无' + '更新股票';
          Modal.info({
            title: modalTitle,
            content: (
              <>
                {response.data.map((divident: string) => (
                  <Row>{divident}</Row>
                ))}
              </>
            ),
          });
        } else if (response.status == 302) {
          history.push('/login');
        }
        setDividentLoading(false);
      },
    });
  };

  const gotoSysAdmin = () => {
    location.href = 'sys/admin'
  }

  return (
    <>
      <ProCard gutter={[0, 16]}>
        <Button
          type="primary"
          style={{
            margin: 8,
          }}
          onClick={dividentClick}
          loading={dividentLoading}
        >
          更新除权信息
        </Button>
        <Button
          type="primary"
          onClick={gotoSysAdmin}
          style={{
            margin: 8,
          }}
        >
          管理
        </Button>
      </ProCard>
    </>
  );
};
