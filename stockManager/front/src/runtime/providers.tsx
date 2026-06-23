import React, { useLayoutEffect } from 'react';
import { ConfigProvider, App } from 'antd';
import { useModel } from '@umijs/max';
import { getThemeConfig, providerComponentConfig } from '@/theme/themeConfig';

function ThemeConfigProvider({ children }: { children: React.ReactNode }) {
  const { actualTheme } = useModel('theme');

  // useLayoutEffect：与 antd token 的重渲染同帧生效，避免切主题瞬间 `[data-theme]`
  // 相关的 less 规则慢一帧（详见 modal/index.less）
  useLayoutEffect(() => {
    document.documentElement.setAttribute('data-theme', actualTheme);
  }, [actualTheme]);

  // 不再用 key={actualTheme}：antd 6 CSS 变量模式下主题可热切换，
  // 强制 remount 会把整棵子树（含 ProLayout/页面）状态清掉，且会让 navTheme/data-theme
  // 慢一帧，造成白天/暗夜切换时 navbar 与页面的视觉异常。
  return (
    <ConfigProvider theme={getThemeConfig(actualTheme)} {...providerComponentConfig}>
      <App>{children}</App>
    </ConfigProvider>
  );
}

export function innerProvider(container: React.ReactNode) {
  return <ThemeConfigProvider>{container}</ThemeConfigProvider>;
}

export { getThemeConfig, lightThemeConfig } from '@/theme/themeConfig';
