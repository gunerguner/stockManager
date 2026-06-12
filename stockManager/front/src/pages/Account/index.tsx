import React from 'react';
import { Avatar, Card, Tag } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { ProCard, ProDescriptions } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';

const ACCESS_LABELS: Record<string, { label: string; color: string }> = {
  admin: { label: '管理员', color: 'red' },
  staff: { label: '员工', color: 'blue' },
  user: { label: '普通用户', color: 'default' },
};

const Account: React.FC = () => {
  const { initialState } = useModel('@@initialState');
  const currentUser = initialState?.currentUser;
  const access = currentUser?.access ?? 'user';
  const accessMeta = ACCESS_LABELS[access] ?? ACCESS_LABELS.user;

  return (
    <div style={{ borderRadius: 8, padding: 16 }}>
      <ProCard>
        <Card style={{ maxWidth: 480, margin: '0 auto' }} styles={{ body: { padding: 24 } }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
            <Avatar size={64} icon={<UserOutlined />} />
            <div>
              <div style={{ fontSize: 20, fontWeight: 600 }}>{currentUser?.name}</div>
              <div style={{ color: 'rgba(0,0,0,0.45)' }}>{currentUser?.username}</div>
            </div>
          </div>
          <ProDescriptions column={1} bordered size="small">
            <ProDescriptions.Item label="用户名">{currentUser?.username}</ProDescriptions.Item>
            <ProDescriptions.Item label="显示名称">{currentUser?.name}</ProDescriptions.Item>
            <ProDescriptions.Item label="角色">
              <Tag color={accessMeta.color}>{accessMeta.label}</Tag>
            </ProDescriptions.Item>
          </ProDescriptions>
        </Card>
      </ProCard>
    </div>
  );
};

export default Account;
