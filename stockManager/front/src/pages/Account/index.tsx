import React from 'react';
import { Avatar, Card, Tag, theme } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { useModel } from '@umijs/max';
import styles from './index.less';

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

  const rows: [string, React.ReactNode][] = [
    ['用户名', user?.username],
    ['显示名称', user?.name],
    ['角色', <Tag style={meta.tag(token)}>{meta.label}</Tag>],
  ];

  return (
    <div className="page-container">
      <Card className={styles.card} styles={{ body: { padding: 24 } }}>
        <div className={styles.header}>
          <Avatar size={64} icon={<UserOutlined />} className={styles.avatar} />
          <div>
            <div className={styles.name}>{user?.name}</div>
            <div className={styles.username}>{user?.username}</div>
          </div>
        </div>
        <div className={styles.table}>
          {rows.map(([label, value]) => (
            <div key={label} className={styles.row}>
              <div className={styles.label}>{label}</div>
              <div className={styles.value}>{value}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Account;
