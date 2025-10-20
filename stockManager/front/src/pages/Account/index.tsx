import React from 'react';
import { Card } from 'antd';
import ProCard from '@ant-design/pro-card';
import { useModel } from 'umi';

/**
 * 账户设置页面
 * 显示当前登录用户的基本信息
 */
const Account: React.FC = () => {
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

export default Account;
