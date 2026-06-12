import React, { useEffect } from 'react';
import { ConfigProvider, App } from 'antd';
import { useModel } from '@umijs/max';
import { getThemeConfig } from '@/theme/themeConfig';

function ThemeConfigProvider({ children }: { children: React.ReactNode }) {
  const { actualTheme } = useModel('theme');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', actualTheme);
  }, [actualTheme]);

  return (
    <ConfigProvider key={actualTheme} theme={getThemeConfig(actualTheme)}>
      <App>{children}</App>
    </ConfigProvider>
  );
}

export function innerProvider(container: React.ReactNode) {
  return <ThemeConfigProvider>{container}</ThemeConfigProvider>;
}

export { getThemeConfig, lightThemeConfig } from '@/theme/themeConfig';
