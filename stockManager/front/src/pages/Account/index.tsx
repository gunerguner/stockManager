import React from 'react';
import { Avatar, Card, Tag, theme } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { useModel } from '@umijs/max';
import '@/components/Common/index.less';

type Token = ReturnType<typeof theme.useToken>['token'];

// 用对象映射替代 switch，数据驱动更精简
const ACCESS_META: Record<string, { label: string; tag: (t: Token) => React.CSSProperties }> = {
  admin: { label: '管理员', tag: (t) => ({ background: t.colorErrorBg, color: t.colorError, borderColor: t.colorErrorBorder }) },
  staff: { label: '员工', tag: (t) => ({ background: t.colorInfoBg, color: t.colorInfo, borderColor: t.colorInfoBorder }) },
  user: { label: '普通用户', tag: (t) => ({ background: t.colorFillQuaternary, color: t.colorText, borderColor: t.colorBorder }) },
};

const Account: React.FC = () => {
  const { initialState } = useModel('@@initialState');
  const user = initialState?.currentUser;
  const meta = ACCESS_META[user?.access ?? 'user'];
  const { token } = theme.useToken();
  const bd = `1px solid ${token.colorBorderSecondary}`;

  const rows: [string, React.ReactNode][] = [
    ['用户名', user?.username],
    ['显示名称', user?.name],
    ['角色', <Tag style={meta.tag(token)}>{meta.label}</Tag>],
  ];

  return (
    <div className="page-container">
      <Card
        style={{ maxWidth: 480, margin: '0 auto', borderColor: token.colorBorderSecondary }}
        styles={{ body: { padding: 24 } }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
          <Avatar size={64} icon={<UserOutlined />} style={{ backgroundColor: token.colorPrimary, color: '#fff' }} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 600, color: token.colorText }}>{user?.name}</div>
            <div style={{ color: token.colorTextSecondary }}>{user?.username}</div>
          </div>
        </div>
        <div style={{ borderRadius: token.borderRadius, overflow: 'hidden', border: bd }}>
          {rows.map(([label, value], idx) => (
            <div key={label} style={{ display: 'flex', borderBottom: idx < rows.length - 1 ? bd : 'none' }}>
              <div style={{ width: 100, padding: '10px 16px', background: token.colorFillQuaternary, color: token.colorTextSecondary, fontSize: 14, borderRight: bd }}>
                {label}
              </div>
              <div style={{ flex: 1, padding: '10px 16px', color: token.colorText, fontSize: 14 }}>
                {value}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Account;
