import { useEffect } from 'react';
import { useModel } from '@umijs/max';
import defaultSettings from '../../config/defaultSettings';
import { PRIMARY_COLOR } from '@/theme/themeConfig';

/** 将 theme model 同步到 ProLayout initialState.settings */
const ThemeLayoutSync: React.FC = () => {
  const { actualTheme } = useModel('theme');
  const { setInitialState } = useModel('@@initialState');

  useEffect(() => {
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
