import React, { useEffect } from 'react';
import { ConfigProvider, theme, App } from 'antd';
import { useModel } from '@umijs/max';

function ThemeConfigProvider({ children }: { children: React.ReactNode }) {
  const { actualTheme } = useModel('theme');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', actualTheme);
  }, [actualTheme]);

  return (
    <ConfigProvider
      theme={{
        algorithm: actualTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: { colorPrimary: '#1890ff' },
      }}
    >
      <App>{children}</App>
    </ConfigProvider>
  );
}

export function innerProvider(container: React.ReactNode) {
  return <ThemeConfigProvider>{container}</ThemeConfigProvider>;
}
