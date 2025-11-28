import React, { useState, useEffect } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Alert, message, ConfigProvider, theme } from 'antd';
import ProForm, { ProFormText } from '@ant-design/pro-form';
import { Link, history, useModel } from '@umijs/max';

import Footer from '@/components/Footer';
import { login } from '@/services/api';
import { RESPONSE_STATUS } from '@/utils/constants';
import styles from './index.less';

// ==================== 工具函数 ====================

/** 跳转到目标页面 */
const redirectTo = (delay = 10) => {
  setTimeout(() => {
    const redirect = new URLSearchParams(window.location.search).get('redirect');
    history?.push(redirect || '/');
  }, delay);
};

// ==================== 子组件 ====================

/** 登录错误提示 */
const LoginMessage: React.FC<{ content: string }> = ({ content }) => (
  <Alert className={styles.loginMessage} message={content} type="error" showIcon />
);

// ==================== 主组件 ====================

const Login: React.FC = () => {
  const [submitting, setSubmitting] = useState(false);
  const [loginError, setLoginError] = useState(false);
  const { initialState, setInitialState } = useModel('@@initialState');
  const { resetStockData } = useModel('stocks');

  // 强制使用浅色主题 & 已登录用户自动跳转
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'light');

    // 延迟检查登录状态，确保登出操作完成
    const timer = setTimeout(() => {
      if (initialState?.currentUser) {
        message.info('您已登录，正在跳转...');
        redirectTo(500);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [initialState?.currentUser]);

  /** 处理登录提交 */
  const handleSubmit = async (values: API.LoginParams) => {
    setSubmitting(true);
    setLoginError(false);

    try {
      const result = await login(values);

      if (result.status === RESPONSE_STATUS.SUCCESS) {
        message.success('登录成功！');
        resetStockData();

        // 获取并设置用户信息
        const userInfo = await initialState?.fetchUserInfo?.();
        if (userInfo) {
          setInitialState((s) => ({ ...s, currentUser: userInfo }));
        }

        redirectTo();
        return;
      }

      setLoginError(true);
    } catch {
      message.error('登录失败，请重试！');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: { colorPrimary: '#1890ff' },
      }}
    >
      <div className={styles.container}>
        <div className={styles.content}>
          {/* 头部 */}
          <div className={styles.top}>
            <div className={styles.header}>
              <Link to="/">
                <span className={styles.title}>Stock Manager</span>
              </Link>
            </div>
            <div className={styles.desc}>股市有风险，入市需谨慎</div>
          </div>

          {/* 登录表单 */}
          <div className={styles.main}>
            <ProForm
              submitter={{
                searchConfig: { submitText: '登录' },
                render: (_, dom) => dom.pop(),
                submitButtonProps: {
                  loading: submitting,
                  size: 'large',
                  className: styles.submitButton,
                },
              }}
              onFinish={handleSubmit}
            >
              {loginError && <LoginMessage content="账户或密码错误" />}

              <ProFormText
                name="username"
                placeholder="用户名"
                fieldProps={{
                  size: 'large',
                  prefix: <UserOutlined className={styles.prefixIcon} />,
                }}
                rules={[{ required: true, message: '请输入用户名!' }]}
              />

              <ProFormText.Password
                name="password"
                placeholder="密码"
                fieldProps={{
                  size: 'large',
                  prefix: <LockOutlined className={styles.prefixIcon} />,
                }}
                rules={[{ required: true, message: '请输入密码!' }]}
              />
            </ProForm>
          </div>
        </div>
        <Footer />
      </div>
    </ConfigProvider>
  );
};

export default Login;
