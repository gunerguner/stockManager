import React, { useState, useEffect } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Alert, message, Card } from 'antd';
import { ProForm, ProFormText } from '@ant-design/pro-components';
import { Link, history, useModel } from '@umijs/max';

import Footer from '@/components/Footer';
import { login } from '@/services/api';
import { isApiSuccess } from '@/utils/api';
import styles from './index.less';

const redirectTo = (delay = 10) => {
  setTimeout(() => {
    const redirect = new URLSearchParams(window.location.search).get('redirect');
    history?.push(redirect || '/');
  }, delay);
};

const LoginMessage: React.FC<{ content: string }> = ({ content }) => (
  <Alert className={styles.loginMessage} message={content} type="error" showIcon />
);

const Login: React.FC = () => {
  const [submitting, setSubmitting] = useState(false);
  const [loginError, setLoginError] = useState(false);
  const { initialState, setInitialState } = useModel('@@initialState');
  const { resetStockData } = useModel('stocks');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'light');

    const timer = setTimeout(() => {
      if (initialState?.currentUser) {
        message.info('您已登录，正在跳转...');
        redirectTo(500);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [initialState?.currentUser]);

  const handleSubmit = async (values: API.LoginParams) => {
    setSubmitting(true);
    setLoginError(false);

    try {
      const result = await login(values);

      if (isApiSuccess(result)) {
        message.success('登录成功！');
        resetStockData();

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
    <div className={styles.container}>
      <div className={styles.layout}>
        <div className={styles.brandPanel}>
          <h1 className={styles.brandTitle}>Stock Manager</h1>
          <p className={styles.brandDesc}>个人持仓与盈亏记录</p>
          <p className={styles.brandSlogan}>股市有风险，入市需谨慎</p>
        </div>

        <div className={styles.formPanel}>
          <Card className={styles.loginCard} variant="borderless">
            <div className={styles.formHeader}>
              <Link to="/">
                <span className={styles.formTitle}>登录</span>
              </Link>
            </div>

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
          </Card>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
