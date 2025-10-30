import React, { useState, useCallback } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Alert, message } from 'antd';
import ProForm, { ProFormText } from '@ant-design/pro-form';
import { Link, history, useModel } from '@umijs/max';

import Footer from '@/components/Footer';
import { login } from '@/services/api';
import styles from './index.less';

interface LoginMessageProps {
  content: string;
}

const LoginMessage: React.FC<LoginMessageProps> = ({ content }) => (
  <Alert className={styles.loginMessage} message={content} type="error" showIcon />
);

/** 此方法会跳转到 redirect 参数所在的位置 */
const goto = () => {
  if (!history) return;
  setTimeout(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const redirect = urlParams.get('redirect');
    history.push(redirect || '/');
  }, 10);
};

const Login: React.FC = () => {
  const [submitting, setSubmitting] = useState(false);
  const [userLoginState, setUserLoginState] = useState<API.LoginResult | undefined>(undefined);
  const { initialState, setInitialState } = useModel('@@initialState');

  const fetchUserInfo = useCallback(async () => {
    const userInfo = await initialState?.fetchUserInfo?.();
    if (userInfo) {
      await setInitialState((s) => ({
        ...s,
        currentUser: userInfo,
      }));
    }
  }, [initialState?.fetchUserInfo, setInitialState]);

  const handleSubmit = useCallback(async (values: API.LoginParams) => {
    setSubmitting(true);
    try {
      const msg = await login({ ...values });
      if (msg.status === 1) {
        message.success('登录成功！');
        await fetchUserInfo();
        goto();
        return;
      }
      setUserLoginState(msg);
    } catch (error) {
      message.error('登录失败，请重试！');
    }
    setSubmitting(false);
  }, [fetchUserInfo]);

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.top}>
          <div className={styles.header}>
            <Link to="/">
              <span className={styles.title}>Stock Manager</span>
            </Link>
          </div>
          <div className={styles.desc}>股市有风险，入市需谨慎</div>
        </div>

        <div className={styles.main}>
          <ProForm
            submitter={{
              searchConfig: {
                submitText: '登录',
              },
              render: (_, dom) => dom.pop(),
              submitButtonProps: {
                loading: submitting,
                size: 'large',
                className: styles.submitButton,
              },
            }}
            onFinish={async (values) => {
              handleSubmit(values as API.LoginParams);
            }}
          >
            {userLoginState?.status === 0 && <LoginMessage content="账户或密码错误" />}
            <ProFormText
              name="username"
              fieldProps={{
                size: 'large',
                prefix: <UserOutlined className={styles.prefixIcon} />,
              }}
              placeholder="用户名: "
              rules={[
                {
                  required: true,
                  message: '请输入用户名!',
                },
              ]}
            />
            <ProFormText.Password
              name="password"
              fieldProps={{
                size: 'large',
                prefix: <LockOutlined className={styles.prefixIcon} />,
              }}
              placeholder="密码: "
              rules={[
                {
                  required: true,
                  message: '请输入密码！',
                },
              ]}
            />
          </ProForm>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Login;
