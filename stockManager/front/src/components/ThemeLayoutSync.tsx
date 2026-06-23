import { useLayoutEffect } from 'react';
import { useModel } from '@umijs/max';
import defaultSettings from '../../config/defaultSettings';
import { PRIMARY_COLOR } from '@/theme/themeConfig';

/** 将 theme model 同步到 ProLayout initialState.settings */
const ThemeLayoutSync: React.FC = () => {
  const { actualTheme } = useModel('theme');
  const { setInitialState } = useModel('@@initialState');

  // useLayoutEffect：与 antd token 的切换同帧落盘 navTheme，避免切主题瞬间
  // ProLayout 拿着旧 navTheme 渲染一帧（navbar 与页面不一致）
  useLayoutEffect(() => {
    const navTheme = actualTheme === 'dark' ? 'realDark' : 'light';

    setInitialState((state) => ({
      ...state,
      settings: {
        ...defaultSettings,
        ...state?.settings,
        navTheme,
        colorPrimary: PRIMARY_COLOR,
        fixedHeader: true,
      },
    }));
  }, [actualTheme, setInitialState]);

  return null;
};

export default ThemeLayoutSync;
