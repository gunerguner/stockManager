import React from 'react';

import { Card } from 'antd';

import ProCard from '@ant-design/pro-card';
import { useModel } from 'umi';

export default (): React.ReactNode => {
  const { initialState } = useModel('@@initialState');

  const currentUser = initialState?.currentUser;
  return (
    <>
      <ProCard gutter={[0, 16]}>
        <Card title={currentUser?.name + ',  你好'} style={{ width: 300 }}>
          <p>{'用户名： ' + currentUser?.username}</p>
          <p>{'角色： ' + currentUser?.access}</p>
        </Card>
      </ProCard>
    </>
  );
};
