import React, { useState, useCallback, useEffect } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Alert, message, ConfigProvider, theme } from 'antd';
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


const goto = (options?: { delay?: number; showMessage?: boolean; messageText?: string }) => {
  if (!history) return;
  
  const { delay = 10, showMessage = false, messageText = '正在跳转...' } = options || {};
  
  if (showMessage) {
    message.info(messageText);
  }
  
  setTimeout(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const redirect = urlParams.get('redirect');
    history.push(redirect || '/');
  }, delay);
};

const Login: React.FC = () => {
  const [submitting, setSubmitting] = useState(false);
  const [userLoginState, setUserLoginState] = useState<API.LoginResult | undefined>(undefined);
  const { initialState, setInitialState } = useModel('@@initialState');
  const { resetStockData } = useModel('stocks');

  // 登录页面强制使用浅色主题，不受全局主题影响
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'light');
    
    // 组件卸载时恢复全局主题（如果需要）
    return () => {
      // 这里不需要恢复，因为离开登录页面后会重新应用全局主题
    };
  }, []);

  // 检查用户是否已登录，如果已登录则重定向
  // 延迟检查，确保登出操作的状态更新已完成（登出等待50ms + 这里延迟100ms = 150ms足够）
  useEffect(() => {
    // 延迟检查，确保登出操作的状态更新已完成
    const checkTimer = setTimeout(() => {
      if (initialState?.currentUser) {
        goto({ 
          delay: 500, 
          showMessage: true, 
          messageText: '您已登录，正在跳转...' 
        });
      }
    }, 100);

    return () => {
      clearTimeout(checkTimer);
    };
  }, [initialState?.currentUser]);

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
        // 重置股票数据状态，确保重新登录后能刷新数据
        resetStockData();
        await fetchUserInfo();
        goto();
        return;
      }
      setUserLoginState(msg);
    } catch (error) {
      message.error('登录失败，请重试！');
    }
    setSubmitting(false);
  }, [fetchUserInfo, resetStockData]);

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm, // 强制使用浅色主题
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
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
    </ConfigProvider>
  );
};

export default Login;
